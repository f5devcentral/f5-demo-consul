#!/bin/sh
python register.py --host 10.1.1.4 --service f5-demo-app --service-id f5-demo-app1 --action deregister
python register.py --host 10.1.1.6 --service f5-demo-app --service-id f5-demo-app2 --action deregister
python register.py --host 10.1.1.7 --service f5-demo-app --service-id f5-demo-app3 --action deregister
