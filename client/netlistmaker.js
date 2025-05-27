const fs = require('fs'); 


function readJsonFile(filePath) {
    try {
        const data = fs.readFileSync(filePath, 'utf8');
        const jsonData = JSON.parse(data);
        return jsonData;
    }   catch (err){
        console.error('Error reading or parsing the file:', err);
        return null;
    }
}

function createHashMap(array) {
    const hashMap = {};
    array.forEach((item, index) => {
      hashMap[item.id] = index;
    });
    return hashMap;
}

function findNodeByIDinHashMap(nodes, hashmap, id){  
    //faster version
    return nodes[hashmap[id]];
}

function findNodeByID(nodes, id){  
    return nodes.find((element, index, arr) => (element.id === id));
  }

function map_the_nodes(graph_data) {
    //data is stored according to its ID
    const nodeMap = new Map(graph_data.nodes.map(node => [node.id, node]));
    const edgeMap = new Map(graph_data.edges.map(edge => [edge.id, edge]));
    for (const element of nodeMap){
        if (!('parentNode' in element [1])){
        element[1].depth = null;
        element[1].preceding_ids = get_preceding_node_ids(element[1].id, nodeMap, edgeMap);
        }
    }
    return {node_map : nodeMap, edge_map : edgeMap};
}

function get_parent_node_id(id, node_map){
    if (!(node_map.has(id))){
        return undefined;
    };
    let node = node_map.get(id);
    if ('parentNode' in node){
        return node.parentNode;
    };
    return id;
}

function get_output_children_ids(id, node_map){
    return [...node_map]
        .filter(([key, value]) => value.parentNode === id && value.type === 'input')
        .map(([key]) => key);
}

function get_input_children_ids(id, node_map){
    const node = node_map.get(id);
    if ((node.type === 'output') && !('parentNode' in node)){
        return [node.id];
    }
    return [...node_map]
        .filter(([key, value]) => value.parentNode === id && value.type === 'output')
        .map(([key]) => key);
}

function get_input_ids(node_map){
    return [...node_map]
        .filter(([key, value]) => ((value.type === 'input') && !('parentNode' in value)))
        .map(([key]) => key);
}

function get_output_ids(node_map){
    return [...node_map]
        .filter(([key, value]) => ((value.type === 'output') && !('parentNode' in value)))
        .map(([key]) => key);
}

function map_to_obj(cmap, item_f){  
    const obj = new Object();
    for (const pair of cmap){   
        obj[pair[0]] = item_f(pair[1]);
    };
    return obj;
}

function get_preceding_node_ids(id, node_map, edge_map){
    let arr = [];
    for (const cid of get_input_children_ids(id, node_map)){
        let edg = [...edge_map]
        .filter(([key, value]) => value.target === cid)
        .map(([key]) => key);
        if (edg.length==0){continue};
        let pid = get_parent_node_id(edge_map.get(edg[0]).source, node_map);
        arr.push(pid);
    }
    return arr
}

function get_depth (id, node_map, edge_map) {
    // node = input node
    let node = node_map.get(id);
    if ((node.type === 'input') && !('parentNode' in node)){
        node.depth = 0;
        return 0;
    };

    if ((node.type === "output") && !("parentNode" in node)){
        node.depth = -1;
        return -1;
    };

    //node has certain depth -> return the value
    if (node.depth != null){
        //console.log(node.depth)
        return node.depth;
    }

    let max_depth = 0;
    for (const element of node.preceding_ids){
        let depth = get_depth(element, node_map, edge_map);
        if (depth >= max_depth){
            max_depth = depth;
        }
    }
    node.depth = max_depth+1;
    return node.depth;
}

function assign_depths(node_map, edge_map){
    let d = 0;
    const layer_id_map = new Map();
    layer_id_map.set(0, []);
    let n = 0;
    let depths=[];
    for (const element of node_map){
        if (!('parentNode' in element [1])){
            d = get_depth(element[1].id, node_map, edge_map);
            if (!(layer_id_map.has(d))){
                layer_id_map.set(d, []);
                n++;
            };
            layer_id_map.get(d).push(element[1].id);
        };
    };
    let sorted_map = new Map([...layer_id_map.entries()].sort())
    sorted_map.get(0).sort() //sort first objects in the first layer by ID
    //sorted_map.set(n, layer_id_map.get(-1).sort()); //assign output nodes to last layer
    if (layer_id_map.has(-1) && Array.isArray(layer_id_map.get(-1))) {
        sorted_map.set(n, layer_id_map.get(-1).sort());
    } else {
        console.warn("layer_id_map.get(-1) is undefined or not an array");
        sorted_map.set(n, []); // Assign an empty array if undefined
    }
    sorted_map.delete(-1); //delete auxliary -1th layer
    //update depth of nodes in the last layer
    for (const node_id of sorted_map.get(n)){
        node_map.get(node_id).depth = n;
    }
    return {
        'layer_map' : sorted_map,
        'layer_number' : n
    }
}

function assign_mode_numbers_in_layer(layer, layer_info, node_map, edge_map){
    let i = 0;
    let aux_array_in  = [];
    let aux_array_out  = [];
    let edg = [];
    let mode_in_width = 0;
    let mode_out_width = 0;
    const aux_set_out = new Set();
    let prev_mode_no = null;
    let node = null;
    //assigning modes for layer 0 
    
    if (layer == 0){
        for (const node_id of layer_info.layer_map.get(0)){
            const hasEdges = [...edge_map].some(([key, value]) => value.source === node_id);
            //this part skips unconnected input nodes
            if (!hasEdges) {
                continue;
            }

            node = node_map.get(node_id);
            node.output_mode_no = i;
            i++;
            mode_out_width++; 

        }
    }
    else {
        for (const node_id of layer_info.layer_map.get(layer-1)){
            node = node_map.get(node_id);
            //skips if the input mode does not have any output defined
            if (!node.output_mode_list || node.output_mode_list.length === 0) {
                continue;
            }

            if (node.type === 'input'){
                aux_set_out.add(node.output_mode_no);
            }
            else {
                for (const mode_no of node.output_mode_list){
                    if (mode_no != null){
                        aux_set_out.add(mode_no);
                    };
                };
            };
        };
        if (layer_info.orphan_map.has(layer-1)){
            for (const mode_no of layer_info.orphan_map.get(layer-1)){
                aux_set_out.add(mode_no);
            };
        };
        //loop over all components from all the layers
        for (const node_id of layer_info.layer_map.get(layer)){
            //loop over the children
            aux_array_in = [];
            //assign inputs by looking at the preceding nodes and copying the outputs
            for (const child_id of get_input_children_ids(node_id, node_map)){
                //look at edges, find the edge which has the target here                     
                edg = [...edge_map]
                .filter(([key, value]) => value.target === child_id)
                .map(([key, value]) => value.source); //edges that are connected
                if (edg.length == 0){
                    aux_array_in.push(null);
                    continue;
                }
                else if(edg.length>1){
                    throw new Error("Child input node is connected to more than 1 edge."); // Throws a new Error object
                };                  
                prev_mode_no = node_map.get(edg[0]).output_mode_no;
                //assign mode number to child node
                node_map.get(child_id).input_mode_no = prev_mode_no;
                aux_array_in.push(prev_mode_no);
                mode_in_width++;
                aux_set_out.delete(prev_mode_no);
                //assign outputs
            }
            node_map.get(node_id).input_mode_list = aux_array_in;
        }                        
        layer_info.orphan_map.set(layer, new Set(aux_set_out));
        //assign output by enumeration of connected components
        for (const node_id of layer_info.layer_map.get(layer)){
            aux_array_out = [];
            for (const child_id of get_output_children_ids(node_id, node_map)){
                //look at edges, find the edge which has the target here            
                edg = [...edge_map]
                .filter(([key, value]) => value.source === child_id)
                .map(([key, value]) => value.source); //edges that are connected
                if (edg.length == 0){
                    aux_array_out.push(null);
                    continue;
                }
                else if(edg.length>1){
                    throw new Error("Child output node is connected to more than 1 edge."); // Throws a new Error object
                };
                while (aux_set_out.has(i)){
                    i++;
                }
                node_map.get(child_id).output_mode_no = i;
                aux_array_out.push(i);                
                i++;
                mode_out_width++;
            }
            node_map.get(node_id).output_mode_list = aux_array_out;
        }
        
    }
    return {'mode_in_width' : mode_in_width, 'mode_out_width' : mode_out_width}
}

function assign_mode_numbers(layer_info, node_map, edge_map){
    const winfo = new Map();
    layer_info.orphan_map = new Map();
    for (let i = 0; i<layer_info.layer_number+1; i++) {
        let width_info = assign_mode_numbers_in_layer(i, layer_info, node_map, edge_map);
        winfo.set(i, width_info);
    };
    layer_info.winfo = winfo; //save information about layer widths
}

function replacer(key, value){
    if(value instanceof Array)
        return JSON.stringify(value);
     return value
}

function writeAndFormatJsonFile(filePath, data) {
    //creates and prettifies JSON file 
    jsonFile = JSON.stringify(data, replacer, "\t").replace(/\"\[/g, '[')
    .replace(/\]\"/g,']')
    const dataFix = /"data": \{\s*"(\w+)": (.+?)\s*\}/g;
    jsonFile = jsonFile.replace(dataFix, '"data": {"$1": $2}');
    jsonFile['newKey'] = 'newValue';
    fs.writeFileSync(filePath, jsonFile);
  }

function create_netlist(graph_data, layer_info, parsedData){
    //netlist = new Object();
    //arr1 = [];
    //unconnected_nodes = [];
    //for (key of graph_data.node_map){
    let netlist = new Object();
    let arr1 = [];
    let unconnected_nodes = [];
    let node = null;
    let depth = null;
    //for (const key of graph_data.node_map){
    for (const key of graph_data.node_map){
        //key [0] = id, key [1] = node (with the id of key[0])
        if (!('parentNode' in key [1])){
            node = findNodeByID(parsedData.nodes, key[0]);
            depth = get_depth (node.id, graph_data.node_map, graph_data.edge_map);

            if (node.type != 'input'){
                if (node.type != 'output'){
                    arr1.push([depth, key[0]]);
                    //this part deletes nodes that are at the start/end of the unconnected chain of nodes
                    if (node.input_mode_list.includes(null) && !node.input_mode_list.some(item => typeof item === 'number')){
                        arr1.pop();
                        unconnected_nodes.push(node.id);
                    }; 
                    if (node.output_mode_list.includes(null) && !node.output_mode_list.some(item => typeof item === 'number')){
                        arr1.pop();
                        unconnected_nodes.push(node.id);     
                    }; 
                };
            };
        };
    };
    
    arr1.forEach((subarray, index) => {
        subarray.push(index); // Add the index as the third element
    });
    for (let y = 0; y < arr1.length; y++){
        for (let i = 0; i < arr1.length; i++){
            node = findNodeByID(parsedData.nodes, arr1[i][1]);
            for (let j = 0; j < unconnected_nodes.length; j++){
                deleted_id = unconnected_nodes[j];
                if (node.preceding_ids.includes(deleted_id)){
                    arr1.splice(arr1[i][2],1); //deletes the node that comes after one of the deleted ones
                    arr1.forEach((subarray, index) => {
                        subarray.splice(2, 1, index); // updates the indices of our array 
                    });
                    unconnected_nodes.push(node.id);

                };
            };
        };   
    };

    arr1.sort((a, b) => a[0] - b[0]);
    

    for (let i = 0; i < arr1.length; i++){
        node = findNodeByID(parsedData.nodes, arr1[i][1]);
        depth = get_depth (node.id, graph_data.node_map, graph_data.edge_map);
        const set = layer_info.orphan_map.get(depth);
        let valuesArray = [...set];
        netlist [arr1[i][1]]= {
            type : node.type,
            input_modes : node.input_mode_list,
            output_modes : node.output_mode_list,
            layer : depth,
            data : node.data,
            unused_nodes_in_layer : valuesArray,
        };
    };
    return {
        netlist: netlist,
    };
}

function analyze_graph(parsedData){
    graph_data = map_the_nodes(parsedData);
    const layers_data = assign_depths(graph_data.node_map, graph_data.edge_map);
    assign_mode_numbers(layers_data, graph_data.node_map, graph_data.edge_map);
    const netlist = create_netlist(graph_data, layers_data, parsedData);
    
    return netlist;
}


export {analyze_graph, map_the_nodes, assign_depths, get_depth, assign_mode_numbers, create_netlist};


