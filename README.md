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

OVERWRITE_DOCKERFILE=yes /bin/bash ../kubemaya/scripts/kubemaya.sh package sergioarmgpl kamidar v1 arm64

sudo /bin/bash /opt/k3s/scripts/kubemaya.sh deploy_app kamidar 8080

Activate multiarch
https://www.docker.com/blog/multi-arch-build-and-images-the-simple-way/
https://github.com/docker/buildx
https://github.com/tonistiigi/binfmt
https://docs.docker.com/build/building/multi-platform/#install-qemu-manually