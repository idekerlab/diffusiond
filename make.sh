docker build -t diffusion .
docker kill diff
docker rm diff
docker run -d -p 5000:5000 --name diff diffusion
