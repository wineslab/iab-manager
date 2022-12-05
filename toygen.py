import networkx as nx

T = nx.DiGraph()


# 1-2-3-4-5-6-7-8-9-10
# 1 Donor 4 IAB-Nodes 1 UE

T.add_node(0, role='donor', channel=0, prb=106,           index=1)
T.add_node(1, role='mt',    channel=0, prb=106, iab='12', index=2)
T.add_node(2, role='du',    channel=1, prb=106, iab='12', index=3)
T.add_node(3, role='mt',    channel=1, prb=106, iab='34', index=4)
T.add_node(4, role='du',    channel=0, prb=106, iab='34', index=5)
T.add_node(5, role='mt',    channel=0, prb=106, iab='56', index=6)
T.add_node(6, role='du',    channel=1, prb=106, iab='56', index=7)
T.add_node(7, role='mt',    channel=1, prb=106, iab='78', index=8)
T.add_node(8, role='du',    channel=0, prb=106, iab='78', index=9)
T.add_node(9, role='ue',    channel=0, prb=106, index=10)


T.add_edge(1, 0, type='wireless')
T.add_edge(2, 1, type='wired')
T.add_edge(3, 2, type='wireless')
T.add_edge(4, 3, type='wired')
T.add_edge(5, 4, type='wireless')
T.add_edge(6, 5, type='wired')
T.add_edge(7, 6, type='wireless')
T.add_edge(8, 7, type='wired')
T.add_edge(9, 8, type='wireless')


nx.write_graphml(T, 'topologies/toy1.graphml')


T = nx.DiGraph()


# 25 nodes star
# 1 Donor 25 UE

T.add_node(0, role='ue', channel=0, prb=106,           index=1)
T.add_node(1, role='donor', channel=0, prb=106,           index=2)

# for i in range(19):
#     T.add_node(i+1, role='ue',    channel=0, prb=106, index=i+2)
#     T.add_edge(i+1, 0, type='wireless')


nx.write_graphml(T, 'topologies/toy2.graphml')


# 1-2-3-4-5-6-7-8-9-10
# 1 Donor 4 IAB-Nodes 1 UE
# scenario 20056
T = nx.DiGraph()

T.add_node('20_mt', role='donor', channel=0, prb=106,          index=5)
T.add_node('7_mt',  role='mt',    channel=0, prb=106, iab='7', index=21)
T.add_node('7_du',  role='du',    channel=1, prb=106, iab='7', index=22)
T.add_node('3_mt',  role='mt',    channel=1, prb=106, iab='3', index=13)
T.add_node('3_du',  role='du',    channel=0, prb=106, iab='3', index=14)
T.add_node('12_mt', role='ue',    channel=0, prb=106,          index=27)

T.add_node('9_mt',  role='ue',    channel=0, prb=106,          index=23)
T.add_node('4_mt',  role='ue',    channel=0, prb=106,          index=15)
T.add_node('11_mt', role='ue',    channel=1, prb=106,          index=25)


T.add_edge('9_mt',  '20_mt', type='wireless')
T.add_edge('4_mt',  '20_mt', type='wireless')
T.add_edge('7_mt',  '20_mt', type='wireless')
T.add_edge('7_du',  '7_mt', type='wired')
T.add_edge('11_mt', '7_du', type='wireless')
T.add_edge('3_mt',  '7_du', type='wireless')
T.add_edge('3_du',  '3_mt', type='wired')
T.add_edge('12_mt', '3_du', type='wireless')


nx.write_graphml(T, 'topologies/firenze.graphml')


# 1-2-3-4-5-6-7-8-9-10
# 1 Donor 4 IAB-Nodes 1 UE
# scenario 20056
T = nx.DiGraph()

T.add_node('16_mt',  role='donor', channel=0, prb=106,           index=35)
T.add_node('10_mt',  role='mt',   channel=0, prb=106, iab='10', index=3)
T.add_node('10_du',  role='du',   channel=1, prb=106, iab='10', index=4)
T.add_node('1_mt',   role='mt',   channel=1, prb=106, iab='1',  index=9)
T.add_node('1_du',   role='du',   channel=0, prb=106, iab='1',  index=10)
T.add_node('14_mt',  role='mt',   channel=0, prb=106, iab='14', index=31)
T.add_node('14_du',  role='du',   channel=1, prb=106, iab='14', index=32)
T.add_node('21_mt',  role='ue',   channel=1, prb=106,           index=43)


T.add_edge('10_mt',  '16_mt', type='wireless')
T.add_edge('10_du',  '10_mt', type='wired')
T.add_edge('1_mt',  '10_du', type='wireless')
T.add_edge('1_du',  '1_mt', type='wired')
T.add_edge('14_mt',  '1_du', type='wireless')
T.add_edge('14_du',  '14_mt', type='wired')
T.add_edge('21_mt',  '14_du', type='wireless')


nx.write_graphml(T, 'topologies/firenze2.graphml')


# # 1-2-3-4-5-6-7-8-9-10
# # 1 Donor 4 IAB-Nodes 1 UE
# # scenario 20056
T = nx.DiGraph()

T.add_node('d1', role='donor', channel=0, prb=106,          index=1)
T.add_node('u1',  role='ue',    channel=0, prb=106,          index=2)
T.add_node('u2',  role='ue',    channel=0, prb=106,          index=3)
T.add_node('u3',  role='ue',    channel=0, prb=106,          index=4)

T.add_edge('u1',  'd1', type='wireless')


nx.write_graphml(T, 'topologies/firenze_test.graphml')


# 9-3 -69.5 dB @1Ghz  vs -15.6dB su MCHEM   vs 48dB realistici
# 9-31 -53.5 dB @1Ghz  vs -2.8dB su MCHEM vs 35dB realistici'
# 9-31 -65.5 dB @3.6Ghz
