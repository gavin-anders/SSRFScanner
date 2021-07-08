curl -ski http://127.0.0.1:8081/auth/ -X POST -d '{"username":"root","password":"Password1234"}' -H "Content-type: application/json"

curl -ski http://127.0.0.1:8081/api/callback/ -H 'Authorization: Token bc9514f0892368cfd0ea792a977aff55d53e3634' -H "Content-type: application/json"