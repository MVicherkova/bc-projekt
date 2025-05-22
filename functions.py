"""Calculates and multiplies layer matrices from netlist."""
import json
import numpy as np
import sympy as sp
from collections import OrderedDict

def find_input_size(netlist, layer):
    arrays = []

    for key, item in netlist.items():
        # Check if the node contains 'input_modes'
        if 'input_modes' in item and item['layer'] == layer:
            layer = item['layer']
            
            arrays.append((item['input_modes']))
            arrays.append(item['unused_nodes_in_layer'])
            
    if arrays:  # Check if there is any data in arrays
        flat_list = [num for sublist in arrays for num in sublist if num is not None]
        if flat_list:
            highest_element = max(flat_list)
            return highest_element
        else:
            return None
    else:
        return None  # Return None if no matching nodes found

def find_output_size(netlist, layer):
    arrays = []
    
    for key, item in netlist.items():
        last = list(get_layer_info(netlist)[1])[-1]
        #check if there are any more layers after this one. If it is the last one, the
        #function would not work correctly since we cannot see the outputs in our netlist
        if item['layer'] == last:
            if 'output_modes' in item and item['layer'] == layer:
                layer = item['layer']
                
                arrays.append((item['output_modes']))
                arrays.append(item['unused_nodes_in_layer'])
        else: 
            # Check if the node contains 'input_modes'
            if 'output_modes' in item and item['layer'] == layer:
                layer = item['layer']
                arrays.append((item['output_modes']))
                arrays.append(item['unused_nodes_in_layer'])
                
    if arrays:  # Check if there is any data in arrays
        flat_list = [num for sublist in arrays for num in sublist if num is not None]
        if flat_list:
            highest_element = max(flat_list)
            return highest_element
        else:
            return None
    else:
        return None  # Return None if no matching nodes found

# Phase shifts

def sp_posuv(data,phase):
    """Symbolicky vypocita vnitrni matici fazoveho posuvu."""
    num = int(phase.split('-')[-1]) # zjisti cislo soucastky
    matrix = sp.Matrix([sp.exp(1j * sp.symbols(f"phi_{num}"))])
    return matrix

def np_posuv(data,phase):
    """Numericky vypocita vnitrni matici fazoveho posuvu."""
    if data [phase]['data']:
        k = data[phase]['data']['Phase']
    else:
        raise TypeError("There is no data in", phase)
    matrix = np.array ([np.exp(1j * k)])
            
    return matrix

# Beam splitters
def np_mat_BS(data,bs):
    """Numericky vypocita vnitrni matici delice svazku."""
    if data [bs]['data']:
        t = data[bs]['data']['t']
    else:
        raise TypeError("There is no data in", bs)
            
    r = (1-t**2)**0.5
    matrix = np.array([[t,r],[-r,t]])         
            
    return matrix

def sp_mat_BS(data,bs):
    """Symbolicky vypocita vnitrni matici delice svazku."""

    num = int(bs.split('-')[-1])  # zjisti cislo soucastky 
    t = sp.Symbol(f"t_{num}")
    r = sp.Symbol(f"r_{num}")
    matrix = sp.Matrix([[t,r],[-r,t]])
    return matrix

def get_layer_info(netlist):
    layer_components = OrderedDict()
    ipms = OrderedDict()
    for key, item in netlist.items():
        if item['layer'] in layer_components:
            layer_components[item['layer']].append(key)
        else:
            layer_components[item['layer']] = [key]
        if item['layer'] not in ipms:
            ipms[item['layer']] = item['unused_nodes_in_layer']
    return layer_components, ipms

def print_and_multiply_matrices(netlist):
    """Vypocita matice vrstev podle algortmu ze slajdu"""
    layer_components, ipms = get_layer_info(netlist)
    my_matrices = []
    for layer, components in layer_components.items():
        ipm = ipms[layer]
        row = find_output_size(netlist, layer)+1
        cols = find_input_size(netlist, layer)+1
        
        layer_matrix = np.zeros((row, cols), dtype=complex)

        for key in components:
            item = netlist[key]            
            
            for mode in ipm:
                layer_matrix[mode, mode] = 1
            
            if item['type'] == 'phaseshiftnode':
                #zde vytvorime malou matici 
                matrix = np_posuv(netlist, str(key))
                for i, mode_in in enumerate(item['input_modes']):
                    for j, mode_out in enumerate(item['output_modes']):
                        layer_matrix [mode_in, mode_out] = matrix[0]                            
            if item['type'] == 'beamsplitternode':
                matrix = np_mat_BS(netlist, str(key))
                for i, mode_in in enumerate(item['input_modes']):
                    for j, mode_out in enumerate(item['output_modes']):
                        if (mode_in is None) or (mode_out is None):
                            continue
                        layer_matrix[mode_out, mode_in] = matrix[j,i]
       
        my_matrices.append(layer_matrix)
        
    last_layer = list(get_layer_info(netlist)[1])[-1]
    # Multiply elements one by one
    size = find_output_size(netlist, last_layer)
    result = np.eye(size + 1)
    for x in my_matrices[::-1]:
        result = np.dot(result, x)          
    return result

def sympy_print_and_multiply_matrices(netlist):
    """Vypocita symbolicke matice vrstev podle algortmu ze slajdu"""
    layer_components, ipms = get_layer_info(netlist)
    my_matrices = []
    for layer, components in layer_components.items():
        ipm = ipms[layer]
        row = find_output_size(netlist, layer)+1
        cols = find_input_size(netlist, layer)+1
        
        layer_matrix = sp.zeros(row, cols)

        for key in components:
            item = netlist[key]            
            
            for mode in ipm:
                layer_matrix[mode, mode] = 1
            
            if item['type'] == 'phaseshiftnode':
                #zde vytvorime malou matici 
                matrix = sp_posuv(netlist, str(key))
                for i, mode_in in enumerate(item['input_modes']):
                    for j, mode_out in enumerate(item['output_modes']):
                        layer_matrix [mode_in, mode_out] = matrix[0]                            
            if item['type'] == 'beamsplitternode':
                matrix = sp_mat_BS(netlist, str(key))
                for i, mode_in in enumerate(item['input_modes']):
                    for j, mode_out in enumerate(item['output_modes']):
                        if (mode_in is None) or (mode_out is None):
                            continue
                        layer_matrix[mode_out, mode_in] = matrix[j,i]
       
        my_matrices.append(layer_matrix)
        
    last_layer = list(get_layer_info(netlist)[1])[-1]
    # Multiply elements one by one
    size = find_output_size(netlist, last_layer)
    result = sp.eye(size + 1)
    for x in my_matrices[::-1]:
        print(x)
        result = result * x         
    return result
