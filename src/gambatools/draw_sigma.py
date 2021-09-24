from collections import defaultdict
from typing import Any, List, Set

from gambatools.automaton import Automaton
from gambatools.dfa import DFA
from gambatools.nfa import NFA
from gambatools.pda import PDA
from gambatools.tm import TM
from gambatools.text_utility import read_text, write_text


SIGMA_HEADER = r'''<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/sigma.core.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/conrad.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/utils/sigma.utils.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/utils/sigma.polyfills.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/sigma.settings.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/classes/sigma.classes.dispatcher.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/classes/sigma.classes.configurable.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/classes/sigma.classes.graph.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/classes/sigma.classes.camera.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/classes/sigma.classes.quad.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/classes/sigma.classes.edgequad.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/captors/sigma.captors.mouse.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/captors/sigma.captors.touch.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/renderers/sigma.renderers.canvas.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/renderers/sigma.renderers.webgl.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/renderers/sigma.renderers.svg.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/renderers/sigma.renderers.def.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/renderers/canvas/sigma.canvas.labels.def.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/renderers/canvas/sigma.canvas.hovers.def.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/renderers/canvas/sigma.canvas.nodes.def.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/renderers/canvas/sigma.canvas.edges.def.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/renderers/canvas/sigma.canvas.edges.curve.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/renderers/canvas/sigma.canvas.edges.arrow.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/renderers/canvas/sigma.canvas.edges.curvedArrow.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/renderers/canvas/sigma.canvas.edgehovers.def.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/renderers/canvas/sigma.canvas.edgehovers.curve.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/renderers/canvas/sigma.canvas.edgehovers.arrow.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/renderers/canvas/sigma.canvas.edgehovers.curvedArrow.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/renderers/canvas/sigma.canvas.extremities.def.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/middlewares/sigma.middlewares.rescale.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/middlewares/sigma.middlewares.copy.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/misc/sigma.misc.animation.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/misc/sigma.misc.bindEvents.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/misc/sigma.misc.bindDOMEvents.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/src/misc/sigma.misc.drawHovers.js"></script>
<!-- Sigma plugins -->
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/plugins/sigma.layout.forceAtlas2/supervisor.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/plugins/sigma.layout.forceAtlas2/worker.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/plugins/sigma.renderers.edgeLabels/settings.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/plugins/sigma.renderers.edgeLabels/sigma.canvas.edges.labels.def.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/plugins/sigma.renderers.edgeLabels/sigma.canvas.edges.labels.curve.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sigma@1.2.1/plugins/sigma.renderers.edgeLabels/sigma.canvas.edges.labels.curvedArrow.js"></script>
'''

SIGMA_TEMPLATE = r'''
<div id="<CONTAINER>" style="<STYLE>"></div>
<script>
// function for drawing a state
sigma.canvas.nodes.state = function(node, context, settings)
{
  var prefix = settings('prefix') || '';

  context.beginPath();
  context.arc(
    node[prefix + 'x'],
    node[prefix + 'y'],
    node[prefix + 'size'],
    0,
    Math.PI * 2,
    true
  );
  context.fillStyle = node.initial ? 'lightgreen' : 'white';
  context.fill();
  context.strokeStyle = 'black';
  context.stroke();

  if (node.accept)
  {
    var d = 4;
    context.arc(
      node[prefix + 'x'],
      node[prefix + 'y'],
      node[prefix + 'size'],
      0,
      Math.PI * 2,
      true
    );
    context.stroke();
  }
  context.closePath();
};

// function for drawing a state label
sigma.canvas.labels.state = function(node, context, settings)
{
  var fontSize,
      prefix = settings('prefix') || '',
      size = node[prefix + 'size'];

  if (size < settings('labelThreshold'))
    return;

  if (!node.label || typeof node.label !== 'string')
    return;

  fontSize = (settings('labelSize') === 'fixed') ? settings('defaultLabelSize') : settings('labelSizeRatio') * size;

  context.font = (settings('fontStyle') ? settings('fontStyle') + ' ' : '') + fontSize + 'px ' + settings('font');
  context.fillStyle = 'black';

  var labelWidth = context.measureText(node.label).width;
  var labelPlacementX = Math.round(node[prefix + 'x'] - labelWidth / 2);
  var labelPlacementY = Math.round(node[prefix + 'y'] + fontSize / 3);
  context.fillText(node.label, labelPlacementX, labelPlacementY);
};

var s = new sigma(
  {
    renderer: {
      container: document.getElementById('<CONTAINER>'),
      type: 'canvas'
    },
    settings: {
      edgeLabelSize: 'fixed',
      minArrowSize: 15,
      minNodeSize: 18,
      maxNodeSize: 30,
      defaultLabelSize: 14,
      defaultEdgeLabelSize: 16,
    }
  }
);

var graph =
{
  nodes:
  [
    <NODES>
  ],
  edges:
  [
    <EDGES>
  ]
};

s.graph.read(graph);
s.refresh();
s.startForceAtlas2();
window.setTimeout(function() {s.killForceAtlas2()}, 3000);
</script>
'''


HTML_TEMPLATE = r'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>Automaton Visualization</title>
{}
<style>
  html {{ height:100%; }}
  body {{ height:100%; }}
</style>
</head>
<body>
{}
</body>
</html>
'''


def default_html_settings():
    return {'container': 'sigma-container', 'style': 'width:100%; height:100%; background-color:#E1E1E1'}


# {id: 0, label: 'q0', x: Math.random(), y: Math.random(), size: 1, type: 'state', initial: true},
def make_node(id: int, label: str, accept: bool = False, initial: bool = False) -> str:
    attributes = {
        'id': id,
        'label': "'{}'".format(label),
        'x': 'Math.random()',
        'y': 'Math.random()',
        'size': 1,
        'type': "'state'",
    }
    if accept:
        attributes['accept'] = 'true'
    if initial:
        attributes['initial'] = 'true'
    items = ["{}: {}".format(key, value) for (key, value) in attributes.items()]
    return '{{ {} }}'.format(', '.join(items))


#    { id: 0, label: 'a', source: '0', target: '1', color: '#00000', type: 'arrow' },
#    { id: 1, label: 'b', source: '1', target: '0', color: '#00000', type: 'curvedArrow' },
def make_edge(id: int, label: str, source: int, target: int, color: str, type_: str) -> str:
    attributes = {
        'id': id,
        'label': "'{}'".format(label),
        'source': "{}".format(source),
        'target': "{}".format(target),
        'color': "'{}'".format(color),
        'type': "'{}'".format(type_),
    }
    items = ["{}: {}".format(key, value) for (key, value) in attributes.items()]
    return '{{ {} }}'.format(', '.join(items))


def make_html(nodes: List[str], edges: List[str], html_settings=default_html_settings()) -> str:
    text = SIGMA_TEMPLATE
    text = text.replace('<CONTAINER>', html_settings['container'])
    text = text.replace('<STYLE>', html_settings['style'])
    text = text.replace('<NODES>', ',\n    '.join(nodes))
    text = text.replace('<EDGES>', ',\n    '.join(edges))
    return text


def compute_nodes(states: Set[Any], initial_states: Set[Any], final_states: Set[Any] = frozenset([])):
    # compute nodes
    nodes = []
    node_map = {}
    for i, q in enumerate(states):
        initial = q in initial_states
        accept = q in final_states
        nodes.append(make_node(i, q, accept, initial))
        node_map[q] = i
    return nodes, node_map


def automaton_to_sigma(A: Automaton, html_settings=default_html_settings()) -> str:
    initial_states = A.initial_states
    states = A.states
    transitions = A.transitions
    final_states = A.final_states

    nodes, node_map = compute_nodes(states, initial_states, final_states)

    # compute edges
    edge_map = defaultdict(lambda: [])
    for (p, a, q) in transitions:
        edge_map[p, q].append(a)
    edges = []
    for i, ((p, q), labels) in enumerate(edge_map.items()):
        type_ = 'curvedArrow' if (q, p) in edge_map else 'arrow'
        label = ','.join(labels)
        label = label.replace('_', 'ε')
        edges.append(make_edge(i, label, node_map[p], node_map[q], 'black', type_))
    return make_html(nodes, edges, html_settings)


def dfa_to_sigma(D: DFA, html_settings=default_html_settings()) -> str:
    q0 = D.q0
    Q = D.Q
    F = D.F
    delta = D.delta

    nodes, node_map = compute_nodes(Q, {q0}, F)

    # compute edges
    edge_map = defaultdict(lambda: [])
    for (q, a), q1 in delta.items():
        edge_map[q, q1].append(a)
    edges = []
    for i, ((q, q1), labels) in enumerate(edge_map.items()):
        type_ = 'curvedArrow' if (q1, q) in edge_map else 'arrow'
        label = ' '.join(labels)
        edges.append(make_edge(i, label, node_map[q], node_map[q1], 'black', type_))
    return make_html(nodes, edges, html_settings)


def nfa_to_sigma(N: NFA, html_settings=default_html_settings()) -> str:
    q0 = N.q0
    Q = N.Q
    F = N.F
    delta = N.delta
    epsilon = N.epsilon

    nodes, node_map = compute_nodes(Q, {q0}, F)

    # compute edges
    edge_map = defaultdict(lambda: [])
    for (q, a), Q1 in delta.items():
        a = 'ε' if a == epsilon else a
        for q1 in Q1:
            edge_map[q, q1].append(a)
    edges = []
    for i, ((q, q1), labels) in enumerate(edge_map.items()):
        type_ = 'curvedArrow' if (q1, q) in edge_map else 'arrow'
        label = ','.join(labels)
        edges.append(make_edge(i, label, node_map[q], node_map[q1], 'black', type_))
    return make_html(nodes, edges, html_settings)


def pda_to_sigma(P: PDA, html_settings=default_html_settings()) -> str:
    q0 = P.q0
    Q = P.Q
    F = P.F
    delta = P.delta
    epsilon = P.epsilon

    nodes, node_map = compute_nodes(Q, {q0}, F)

    # compute edges
    edge_map = defaultdict(lambda: [])
    for (p, a, u), Q1 in delta.items():
        for (q, v) in Q1:
            a = 'ε' if a == epsilon else a
            u = 'ε' if u == epsilon else u
            v = 'ε' if v == epsilon else v
            edge_map[p, q].append('{},{}→{}'.format(a, u, v))
    edges = []
    for i, ((p, q), labels) in enumerate(edge_map.items()):
        type_ = 'curvedArrow' if (q, p) in edge_map else 'arrow'
        label = ','.join(labels)
        edges.append(make_edge(i, label, node_map[p], node_map[q], 'black', type_))
    return make_html(nodes, edges, html_settings)


def tm_to_sigma(T: TM, html_settings=default_html_settings()) -> str:
    q0 = T.q0
    Q = T.Q
    delta = T.delta
    blank = T.blank

    nodes, node_map = compute_nodes(Q, {q0})

    # compute edges
    edge_map = defaultdict(lambda: [])
    for (p, a), (q, b, d) in delta.items():
        a = '□' if a == blank else a
        b = '□' if b == blank else b
        edge_map[p, q].append('{}→{},{}'.format(a, b, d))
    edges = []
    for i, ((p, q), labels) in enumerate(edge_map.items()):
        type_ = 'curvedArrow' if (q, p) in edge_map else 'arrow'
        label = ' '.join(labels)
        edges.append(make_edge(i, label, node_map[p], node_map[q], 'black', type_))
    return make_html(nodes, edges, html_settings)


def draw_dfa(D: DFA, filename: str) -> None:
    write_text(filename, HTML_TEMPLATE.format(SIGMA_HEADER, dfa_to_sigma(D)))


def draw_nfa(N: NFA, filename: str) -> None:
    write_text(filename, HTML_TEMPLATE.format(SIGMA_HEADER, nfa_to_sigma(N)))
    write_text(filename, SIGMA_HEADER + nfa_to_sigma(N))


def draw_pda(P: PDA, filename: str) -> None:
    write_text(filename, HTML_TEMPLATE.format(SIGMA_HEADER, pda_to_sigma(P)))


def draw_tm(T: TM, filename: str) -> None:
    write_text(filename, HTML_TEMPLATE.format(SIGMA_HEADER, tm_to_sigma(T)))
