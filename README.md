# mayabox
How to use it:  
1. Install requeriments
```
cd kaminar/src
pip3 install -r requirements.txt
```
2. Create the certificates  
```
/bin/bash create_cert.sh
```
3. Run the application  
```
python3 index.py
```


# Compile OpenCV base
1. Install Docker build
```
sudo apt-get install docker-buildx
```
2. Install qemu emulators to support multiarch compilation
```
docker run --privileged --rm tonistiigi/binfmt --install all
```
3. Configure containerd storage
```
echo '{
  "features": {
    "containerd-snapshotter": true
  }
}' > /etc/docker/daemon.json
sudo systemctl restart docker
docker info -f '{{ .DriverStatus }}'
```

4. Build your image
```
docker buildx build \
--push \
--platform linux/arm/v7,linux/arm64/v8,linux/amd64 \ --tag your-username/multiarch-example:buildx-latest .
```

## Build Mayabox
```
OVERWRITE_DOCKERFILE=yes /bin/bash ../kubemaya/scripts/kubemaya.sh package sergioarmgpl kamidar v1 arm64
sudo /bin/bash /opt/k3s/scripts/kubemaya.sh deploy_app kamidar 8080
```

### References
- https://docs.docker.com/engine/storage/containerd/
- https://www.docker.com/blog/multi-arch-build-and-images-the-simple-way/
- https://github.com/docker/buildx
- https://github.com/tonistiigi/binfmt
- https://docs.docker.com/build/building/multi-platform/#install-qemu-manually