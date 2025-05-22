<script setup>
import { onMounted } from 'vue'
import { Position, useNode, useVueFlow } from '@vue-flow/core'

// props were passed from the slot using `v-bind="customNodeProps"`
const props = defineProps(['label'])
const { node } = useNode()
const {updateNodeData} = useVueFlow()

defineEmits(["updateNodeInternals"])

function onTset(event) {
  console.log('transmittance changed');
  console.log(event);
  updateNodeData(node.id, {t : Number.parseFloat(event.target.value)})
}

</script>

<template>
  <div>
  <div>{{ label }}</div>
  <label>T:
  <input type="number" name="transmittance" :value="node.data.t" @input="onTset" min="0" max="1" step="0.1">
  </label>
  </div>
</template>

<style>
input {
  width: 75px;
}

.vue-flow__node-beamsplitternode {
    background: #60a010;
    color: black;
    border: 1px solid #60a010;
    border-radius: 4px;
    box-shadow: 0 0 0 1px #207000;
    padding: 8px;
    height: 180px;
    width: 150px;
}

.vue-flow__node-beamsplitternode.selected {
  border: 1px solid black;
  background: #90c040;
}
</style>