import multiprocessing
import asyncio
import queue
import dataclasses
import uuid

def process_worker (iqueue, oqueue):
  while 1:
    task_spec = iqueue.get()
    task_uuid, task_func, task_args = task_spec
    oqueue.put(make_message_status(task_uuid, 0x01))
    try:
      task_data = task_func(* task_args)
      oqueue.put(make_message_result(task_uuid, task_data))
    except Exception as task_fail:
      oqueue.put(make_message_failed(task_uuid, task_fail))

def make_message_status (task_uuid, value):
  return (task_uuid, 0x01, value)
def make_message_result (task_uuid, value):
  return (task_uuid, 0x02, value)
def make_message_failed (task_uuid, value):
  return (task_uuid, 0x03, value)

@dataclasses.dataclass
class taskspec:
  task_uuid : str
  task_func : object = None
  task_args : object = None
  task_data : object = None
  task_fail : object = None

  # 0x00 waiting
  # 0x01 processing
  # 0x02 finished 
  # ... | 0x04 = 0x06 success
  # ... | 0x08 = 0x0A failed
  status : int = 0x00

class governor (object):
  def __init__ (self, pool_size):
    self._iqueue = multiprocessing.Queue()
    self._oqueue = multiprocessing.Queue()
    self._worker_pool = []
    self._task_buffer = {}

    self._worker_pool_bootstrap(pool_size)
    self._worker_pool_activate()
    # self._watch_oqueue_task = asyncio.run(self._watch_oqueue())
    self._watch_oqueue_task = asyncio.create_task(self._watch_oqueue())

  def _worker_pool_bootstrap (self, pool_size):
    self._worker_pool = [
      multiprocessing.Process(
        target = process_worker,
        args = (self._iqueue, self._oqueue),
        name = f'governor-worker-{index}')
      for index in range(pool_size) ]
  def _worker_pool_terminate (self):
    for worker in self._worker_pool:
      worker.terminate()
  def _worker_pool_activate (self):
    for worker in self._worker_pool:
      worker.start()

  async def _watch_oqueue (self):
    loop = asyncio.get_running_loop()
    while 1:
      if not (packet := await loop.run_in_executor(None, self._watch_oqueue_get)):
        continue

      task_uuid, code, data = packet
      task = self._task_buffer.get(task_uuid)
      if not task:
        continue

      match (code):
        case 0x01:
          task.status = data
        case 0x02:
          task.status = 0x02 | 0x04
          task.task_data = data
        case 0x03:
          task.status = 0x02 | 0x08
          task.task_fail = data

  def _watch_oqueue_get (self):
    try:
      return self._oqueue.get(block = 1, timeout = 1.0)
    except queue.Empty:
      return None

  def _task_uuid (self):
    return str(uuid.uuid4())

  def _worker_pool_submit (self, task):
    task_spec = (task.task_uuid, task.task_func, task.task_args)
    self._iqueue.put(task_spec)

  def submit (self, task_func, task_args):
    task = taskspec(
      task_uuid = self._task_uuid(),
      task_func = task_func,
      task_args = task_args)
    self._task_buffer[task.task_uuid] = task
    self._worker_pool_submit(task)
    return task.task_uuid

  def status (self, task_uuid):
    if not (task := self._task_buffer.get(task_uuid)):
      raise KeyError
    return task.status

  def result (self, task_uuid):
    if not (task := self._task_buffer.get(task_uuid)):
      raise KeyError
    if not (0x02 & task.status):
      raise ValueError
    return task.task_fail, task.task_data

  def remove (self, task_uuid):
    if not (task := self._task_buffer.pop(task_uuid)):
      raise KeyError

