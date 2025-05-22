<script setup>
import { onMounted } from 'vue'
import { Position, useNode, useVueFlow } from '@vue-flow/core'

// props were passed from the slot using `v-bind="customNodeProps"`
const props = defineProps(['label'])
const { node } = useNode()
const {updateNodeData} = useVueFlow()
const emits = defineEmits(["updateNodeInternals"])

function onPset(event) {
  console.log('phaseshift changed');
  console.log(event);
  updateNodeData(node.id, {Phase : Number.parseFloat(event.target.value)})
}

</script>

<template>
  <div>
  <div>{{ label }}</div>
  <label>Shift:
  <input type="number" name="phaseshift" :value="node.data.Phase" @input="onPset" min="0" max="2" step="0.1">
  </label>
  </div>
</template>

<style>
/* Use a purple theme for our custom node */
input {
  width: 75px;
}

.vue-flow__node-phaseshiftnode {
    background: #A020F0;
    color: black;
    border: 1px solid #A020F0;
    border-radius: 4px;
    box-shadow: 0 0 0 1px #207000;
    padding: 8px;
    height: 100px;
    width: 150px;
}

.vue-flow__node-phaseshiftnode.selected {
  border: 1px solid black;
  background: #DA70D6;
}
</style>