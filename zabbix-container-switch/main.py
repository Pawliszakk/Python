#1. Check available images, web and server
#2. Check running images, web and server
#3. if images the same - nothing
#4. list available images and input for image to switch
#5. Switch images in files
#6. Stop Server, Stop Web
#7. Start Server, wait for running, Start Web

# zabbix-server-mysql.container
# docker.io/zabbix/zabbix-server-mysql:7.0.29-ubuntu

# zabbix-web-apache-mysql.container
# docker.io/zabbix/zabbix-web-apache-mysql:7.0.29-ubuntu
import subprocess
import json
from pathlib import Path

def get_current_images(quadlets_path: str, quadlets: list[str]) -> None:
    print("Currently running images: ")
    for quadlet in quadlets:

        try:
            quadlet_data = Path(quadlets_path + quadlet).read_text()
            
            for line in quadlet_data.splitlines():
                if line.startswith("Image="):
                    print(line.removeprefix("Image="))
        except Exception as e:
            print("Something went wrong with quadlets reading...")
            print(e)
            return
    print("\n")
    


def get_available_tags(images: list[str]) -> None:



    print("Checking available images...")
    print("-------------------")
    for image in images:      
        skopeo_command = f"skopeo list-tags docker://{image}"
        print(f"Checking available images for {image}...")
        image_tags = subprocess.run(
            skopeo_command.split(),
            capture_output=True,
            text=True,
            check=True
            )
        image_tags_result = json.loads(image_tags.stdout)
        for tag in image_tags_result["Tags"]:
            if tag.startswith("ubuntu-7.0"):
                print(tag)
        print("\n")

    #Check Web


def main():


    # "/home/zabbix-runner/.config/containers/systemd"
    get_current_images("/home/opawliszak/zabbix-quadlets/",["zabbix-server-mysql.container","zabbix-web-apache-mysql.container"])
    get_available_tags(["docker.io/zabbix/zabbix-server-mysql","docker.io/zabbix/zabbix-web-apache-mysql"])

if __name__ == "__main__":
    main()

