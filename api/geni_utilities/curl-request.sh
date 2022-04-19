#Test with 2 controllers
 curl -i -v -X POST  \
  -H "Content-Type: application/json" \
-d '{"topology":"{\"ctrl\":{\"c0\":{\"s0\":[],\"s1\":[\"h0\"]}, \"c1\":{\"s2\":[],\"s3\":[\"h1\"]}},\"links\":{\"s0\":[\"s1\"],\"s1\":[\"s0\"]},\"num_ctrl\":1,\"num_sw\":2,\"num_h\":1,\"num_link\":3}","decisional_model":"DeepQLearning","num_controllers":1,"data_frequency":1}' \
 "127.0.0.1:8000/api/experiment"

 #nsFnet topology 
  curl -i -v -X POST  \
  -H "Content-Type: application/json" \
-d '{"topology":"{\"ctrl\":{\"c0\":{\"s0\":[\"h0\",\"h1\"],\"s1\":[\"h2\",\"h3\"],\"s2\":[\"h4\",\"h5\"],\"s3\":[],\"s4\":[],\"s5\":[\"h6\",\"h7\"],\"s6\":[],\"s7\":[],\"s8\":[\"h10\",\"h11\"],\"s9\":[\"h14\",\"h15\"],\"s10\":[],\"s11\":[\"h12\",\"h13\"],\"s12\":[\"h16\",\"h17\"],\"s13\":[\"h8\",\"h9\"]}},\"links\":{\"s0\":[\"s1\",\"s2\",\"s5\"],\"s1\":[\"s0\",\"s2\",\"s3\"],\"s2\":[\"s0\",\"s1\",\"s8\"],\"s5\":[\"s0\",\"s10\",\"s6\"],\"s3\":[\"s1\",\"s6\",\"s4\",\"s13\"],\"s8\":[\"s2\",\"s7\",\"s9\"],\"s6\":[\"s3\",\"s5\",\"s7\"],\"s4\":[\"s3\",\"s9\"],\"s13\":[\"s3\",\"s12\"],\"s9\":[\"s4\",\"s8\",\"s11\"],\"s10\":[\"s5\",\"s11\",\"s12\"],\"s7\":[\"s6\",\"s8\"],\"s11\":[\"s9\",\"s10\"],\"s12\":[\"s10\",\"s13\"]},\"num_ctrl\":1,\"num_sw\":14,\"num_h\":18,\"num_link\":56}","decisional_model":"DeepQLearning","num_controllers":1,"data_frequency":1}' \
 "127.0.0.1:8000/api/experiment"
 
 #Basic 4 sw, 6h for iperf script
curl -i -v -X POST  \
-H "Content-Type: application/json" \
-d '{"topology":"{\"ctrl\":{\"c0\":{\"s0\":[],\"s1\":[\"h0\",\"h1\"],\"s2\":[\"h2\",\"h3\"],\"s3\":[\"h4\",\"h5\"]}},\"links\":{\"s0\":[\"s1\",\"s3\"],\"s1\":[\"s0\",\"s2\"],\"s2\":[\"s1\",\"s3\"],\"s3\":[\"s2\",\"s0\"]},\"num_ctrl\":1,\"num_sw\":4,\"num_h\":6,\"num_link\":14}"}' \
  "127.0.0.1:8000/api/topology"

curl -i -v -X POST  \
-H "Content-Type: application/json" \
-d '{"support_switches":"s0","data_frequency":1}' \
 "127.0.0.1:8000/api/ryu"

curl -i -v -X POST  \
-H "Content-Type: application/json" \
-d '{"num_support_switches":1,"op_penalty":300, "helped_switches":"1", "data_frequency":1}' \
 "127.0.0.1:8000/api/model"

curl -i -v -X POST  \
-H "Content-Type: application/json" \
-d '{"iperf_num":"1","traffic_type":"train"}' \
"127.0.0.1:8000/api/traffic"

curl -i -v -X POST  \
-H "Content-Type: application/json" \
-d '{"file":"login"}' \
"127.0.0.1:8000/api/download"

#create topology 8 sw 10 host
  curl -i -v -X POST  \
  -H "Content-Type: application/json" \
-d '{"topology":"{\"ctrl\":{\"c0\":{\"s0\":[\"h0\",\"h1\"],\"s1\":[\"h2\",\"h3\"],\"s2\":[\"h4\",\"h5\"],\"s3\":[],\"s4\":[],\"s5\":[],\"s6\":[\"h6\",\"h7\"],\"s7\":[\"h8\",\"h9\"]}},\"links\":{\"s0\":[\"s1\",\"s2\",\"s3\"],\"s1\":[\"s0\",\"s7\"],\"s2\":[\"s0\",\"s4\",\"s5\"],\"s3\":[\"s0\",\"s6\",\"s7\"],\"s7\":[\"s1\",\"s3\",\"s5\"],\"s4\":[\"s2\",\"s6\"],\"s5\":[\"s2\",\"s6\",\"s7\"],\"s6\":[\"s3\",\"s4\",\"s5\"]},\"num_ctrl\":1,\"num_sw\":8,\"num_h\":10,\"num_link\":32}","decisional_model":"DeepQLearning","num_controllers":1,"data_frequency":1}' \
 "127.0.0.1:8000/api/topology"

 #ryu
   curl -i -v -X POST  \
  -H "Content-Type: application/json" \
-d '{"support_switches":"s3,s5","data_frequency":1}' \
 "127.0.0.1:8000/api/ryu"

curl -i -v -X POST  \
-H "Content-Type: application/json" \
-d '{"num_support_switches":2,"op_penalty":300, "helped_switches":"4,1,2", "data_frequency":1}' \
 "127.0.0.1:8000/api/model"

 #hosts
curl -i -v -X POST  \
-H "Content-Type: application/json" \
-d '{"iperf_num":"15","traffic_type":"train"}' \
"127.0.0.1:8000/api/traffic"


#Download traffic hosts
curl -i -v -X POST  \
-H "Content-Type: application/json" \
-d '{"file":"traffic"}' \
"127.0.0.1:8000/api/download"

curl -i -v -X POST  \
-H "Content-Type: application/json" \
-d '{"file":"reward"}' \
"127.0.0.1:8000/api/download"

curl -i -v -X POST  \
-H "Content-Type: application/json" \
-d '{"file":"latency"}' \
"127.0.0.1:8000/api/download"
 