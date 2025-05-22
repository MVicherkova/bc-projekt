<script setup>
  import { ref, computed, markRaw } from 'vue'
  import { VueFlow, useVueFlow, Position, ConnectionMode} from '@vue-flow/core'
  import { Background } from '@vue-flow/background'
  import BSnode from 'mindmap/BeamSplitterNode.vue'
  import PhaseShiftnode from 'mindmap/PhaseShiftNode.vue'
  import { onMounted, onUnmounted } from 'vue'
  import {map_the_nodes, assign_depths, assign_mode_numbers, create_netlist} from "./netlistmaker.js"

  
  const { onConnect, addEdges, addNodes, getConnectedEdges, removeEdges, getSelectedNodes, toObject, removeNodes, getNodes, onNodesChange, applyNodeChanges} = useVueFlow()
  const text = ref('Type component ID')

  const parsedData = ref(null);

  const nodeTypes = {
    beamsplitternode: markRaw(BSnode),
    phaseshiftnode: markRaw(PhaseShiftnode)
  }
  const bscounter = ref(1)
  const in_mode_counter = ref(2)
  const out_mode_counter = ref(2)
  
  const phasecounter = ref(1)

  const get_bs_subnodes = (my_id) => (
    [{
      id: `subnode-${my_id}-ina`,
      label: 'AIN',
      position: { x: 10, y: 50 },
      type : 'output',
      parentNode: `${my_id}`,
      targetPosition : Position.Left,
      draggable : false,
      style: {width: '50px'}
      },
    {
      id: `subnode-${my_id}-inb`,
      label: 'BIN',
      position: { x: 10, y: 100 },
      type : 'output',
      parentNode: `${my_id}`,
      targetPosition : Position.Left,
      draggable : false,
      style: {width: '50px'}
    },
    {
      id: `subnode-${my_id}-outa`,
      label: 'AOUT',
      position: { x: 80, y: 50 },
      type : 'input',
      parentNode: `${my_id}`,
      sourcePosition : Position.Right,
      draggable : false,
      style: {width: '50px'}
    },
    {
      id: `subnode-${my_id}-outb`,
      label: 'BOUT',
      position: { x: 80, y: 100 },
      type : 'input',
      parentNode: `${my_id}`,
      sourcePosition : Position.Right,
      draggable : false,
      style: {width: '50px'} 
    }])
    
    const get_phase_subnodes = (my_id) => (
      [{
        id: `subnode-${my_id}-in`,
        label: 'IN',
        position: { x: 10, y: 50 },
        type : 'output',
        parentNode: `${my_id}`,
        targetPosition : Position.Left,
        draggable : false,
        style: {width: '50px'}
        },
      {
        id: `subnode-${my_id}-out`,
        label: 'OUT',
        position: { x: 80, y: 50 },
        type : 'input',
        parentNode: `${my_id}`,
        sourcePosition : Position.Right,
        draggable : false,
        style: {width: '50px'} 
      }])
      
    const nodes = ref([
    // nodes

    // an input node, specified by using `type: 'input'`
    { id: 'node-i-A', type: 'input', label: 'In A', position: { x: 10, y: 10 }, connectable: true, animated: true, sourcePosition : Position.Right,   },
    { id: 'node-i-B', type: 'input', label: 'In B', position: { x: 10, y: 50 }, connectable: true, animated: true, sourcePosition : Position.Right},
    {
    id: 'node-bs-1',    
    label: 'BS parent',
    data: {t : 0.6},
    position: { x: 50, y: 100 },
    type: 'beamsplitternode',
    },
    { id: 'node-o-A', type: 'output', label: 'Out A', position: { x: 300, y: 10 }, connectable: true, animated: true, targetPosition : Position.Left},
    { id: 'node-o-B', type: 'output', label: 'Out B', position: { x: 300, y: 50 }, connectable: true, animated: true, targetPosition : Position.Left},
    {
    id: 'node-phase-1',    
    label: 'Phase shift',
    data: {Phase : 1},
    position: { x: 250, y: 100 },
    type: 'phaseshiftnode',
    },
    ])
    const edges = ref([]) 

    onMounted(() => {
      for (var el of nodes.value){
        if (el.type == 'beamsplitternode'){
          addNodes(get_bs_subnodes(el.id))
        };      
      };
    })
    
    onMounted(() => {
      for (var el of nodes.value){
        if (el.type == 'phaseshiftnode'){
          addNodes(get_phase_subnodes(el.id))
        };      
      };
    })

  onConnect((params) => {        
    for (var edge of getConnectedEdges(params.source)){
      removeEdges(edge.id)
    }
    for (var edge of getConnectedEdges(params.target)){
      removeEdges(edge.id)
    }        
    addEdges(params)
  })

  function addBS(){
    bscounter.value = bscounter.value+1;
    addNodes({
      id : `node-bs-${bscounter.value}`,      
      label: `BS${bscounter.value}`,
      position: { x: 10, y: 10 },
      type: 'beamsplitternode',
    });    
    addNodes(get_bs_subnodes(`node-bs-${bscounter.value}`));
  }
  
  function addPhaseShift(){
    phasecounter.value = phasecounter.value+1;
    addNodes({
      id : `node-phase-${phasecounter.value}`,      
      label: `Phase Shift ${phasecounter.value}`,
      position: { x: 100, y: 100 },
      type: 'phaseshiftnode',
    });    
    addNodes(get_phase_subnodes(`node-phase-${phasecounter.value}`));
  }
  
  function addInNode(){
    in_mode_counter.value = in_mode_counter.value+1;
    addNodes({
      id: `node-i-${in_mode_counter.value}`,
      type: 'input',
      label: `In ${in_mode_counter.value}`,
      position: { x: 10, y: 10 },
      connectable: true,
      animated: true,
      sourcePosition : Position.Right
    });
  }  

  function addOutNode(){
    out_mode_counter.value = out_mode_counter.value+1;
    addNodes({
      id: `node-o-${out_mode_counter.value}`,
      type: 'output',
      label: `Out ${out_mode_counter.value}`,
      position: { x: 10, y: 10 },
      connectable: true,
      animated: true,
      targetPosition : Position.Left
    });    
  }    

  function removeSelectedNode(){
      data = JSON.stringify(toObject());
      const JsonData = JSON.parse(data);
      for (element of getSelectedNodes.value) {
        removeNodes(element.id);
        for (el of JsonData.nodes){
          if (el.parentNode === element.id){
            removeNodes(el.id)
          }; 
        };
    };
  }  

  function getChildNodesByID(id){
    const graph = toObject();
    let ids = new Array();
    for (node of graph.nodes){
      if (node.parentNode === id){        
        ids.push(node.id);
      }
    }
    return ids
  }

  function serialize(){
    console.log("Exporting...");
    console.log(toObject());
  }
  
  function download(){
      const blob = new Blob([JSON.stringify(toObject(), undefined, 2)], {type: 'application/json' });
      const a = document.createElement('a');
      
      a.href = URL.createObjectURL(blob);
      a.download = 'vueflowfile.json';
      a.click();
  }


  function printNodesObj(){
      console.log("Node obj");
      console.log(nodes);
      console.log("Node obj value");
      console.log(nodes.value.id);
      console.log("Get nodes");
      console.log(getNodes.value);
  } 

  
  function showNetlist(){
    const string = JSON.stringify(toObject(), undefined, 2);
    const parsedData = JSON.parse(string);
    graph_data = map_the_nodes(parsedData);
    const layers_data = assign_depths(graph_data.node_map, graph_data.edge_map);
    assign_mode_numbers(layers_data, graph_data.node_map, graph_data.edge_map);
    const netlist = create_netlist(graph_data.node_map,layers_data, parsedData);
    return netlist
  }

  //computing numeric martix

  async function saveNetlist () {
    my_object = showNetlist()
    try{
      const response = await fetch('/api/dictionary', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({data: my_object})
      })

      if (response.ok) {
        const result = await response.json()
        console.log(result) //show successful response
      }
      else{
        console.error("Failed to save netlist.", response.status)
      }
    }
    catch (error) {
      console.error(error)
    }
  }

  //computing symbolic matrix 

  async function saveNetlist2 () {
    my_object = showNetlist()
    try{
      const response = await fetch('/api/dictionary1', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({data: my_object})
      })

      if (response.ok) {
        const result = await response.json()
        console.log(result) //show successful response
      }
      else{
        console.error("Failed to save netlist.", response.status)
      }
    }
    catch (error) {
      console.error(error)
    }
  }

  //Deleting node with its subnodes using backspace
  onNodesChange(async (changes) => {
  const nextChanges = []
  for (const change of changes) {
    if (change.type === 'remove') {
      let child_ids = getChildNodesByID(change.id);
      for (id of child_ids){
        removeNodes(child_ids);
      };
      nextChanges.push(change);
      
    } else {
      nextChanges.push(change);
    };
  };
  applyNodeChanges(nextChanges);
})

</script>

<template>
  <div class='wrapper'>
  <button @click="addBS">Add BS</button>
  <button @click="addPhaseShift">Add PhaseShift</button>
  <button @click="addOutNode">Add output mode</button>
  <button @click="addInNode">Add input mode</button>
  <button @click="serialize">Export</button>
  <button @click="download">Download JSON</button>
  <button style="background-color: #dd0000" @click="removeSelectedNode">Remove node</button>
  <button @click="saveNetlist">Create matrix</button>
  <button @click="saveNetlist2">Create symbolic matrix</button>


  <div class="flowframe">
  <VueFlow 
  :nodes="nodes" 
  :edges="edges" 
  :node-types="nodeTypes"
  @connect-start="onConnectStart"
  @connect-end="onConnectEnd"
  :connection-mode=ConnectionMode.Strict
  >
  <Background/>
  </VueFlow>
  </div>
  </div>

</template>


<style>
@import '../node_modules/@vue-flow/core/dist/style.css';
@import '../node_modules/@vue-flow/core/dist/theme-default.css';

/**/
body {
  background-color: #202020;
}
.flowframe {    
    border-style: dotted;
    width: 95%;  
    height: 500px;  
    min-width: 400px;  
    min-height : 300px;
    margin: auto;
}
.wrapper {
  color : white;
  margin: auto;
  width: 75%;  
  background-color: #303030; 
}

</style>