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
import re


def get_current_images(quadlets_path: str, quadlets: list[str]) -> list[str]:
    
    current_images = []
    
    print("Currently running images: ")
    for quadlet in quadlets:

        try:
            quadlet_data = Path(quadlets_path + quadlet).read_text()
            
            for line in quadlet_data.splitlines():
                if line.startswith("Image="):
                    current_images.append(line.removeprefix("Image="))
                    print(line.removeprefix("Image="))
        except Exception as e:
            print("Something went wrong with quadlets reading...")
            print(e)
            return
    print("\n")
    return current_images
    


def get_available_tags(current_images,images: list[str]) -> None:

    current_images_tags = {}


    for image in current_images:
        
        image_tag = image.split(":")[1]
        image_name = image.split(":")[0]
        image_minor_version = 0

        if image_tag.endswith("-ubuntu"):
            image_minor_version = int(image_tag.removesuffix("-ubuntu").removeprefix("7.0."))

        elif image_tag.startswith("ubuntu-"):
            image_minor_version = int(image_tag.removeprefix("ubuntu-7.0."))

        current_images_tags.update({
            image_name: image_minor_version
        })
    for image in images:     
        skopeo_command = f"skopeo list-tags docker://{image}"

        print("Checking available images...")
        print("------------------------------")
 
        image_tags = subprocess.run(
            skopeo_command.split(),
            capture_output=True,
            text=True,
            check=True
            )

        image_tags_result = json.loads(image_tags.stdout)

        newer_tags_than_running = []
        for tag in image_tags_result["Tags"]:

            if re.fullmatch(r"ubuntu-7\.0\.\d+", tag):
                tag_minor_release = int(tag.removeprefix("ubuntu-7.0."))
                if tag_minor_release > current_images_tags[image]:
                    newer_tags_than_running.append(tag_minor_release)
        if len(newer_tags_than_running) > 0:

            for i,tag in enumerate(sorted(newer_tags_than_running,reverse=True),start=1):
                if i <= 5:
                    full_image = f"{image}:ubuntu-7.0.{tag}"
                    print(f"{i}. {full_image}")
            print("\n")
            user_choice = input(f"Please type number of tag to update (1 - len{newer_tags_than_running}): ").strip()
            if user_choice > 0 and user_choice <= len(newer_tags_than_running):
                print(user_choice)


        else:
            print("Newer images than running were not found.")
        print("\n")


    #Check Web


def main():
    # "/home/opawliszak/zabbix-quadlets/"
    # "/home/zabbix-runner/.config/containers/systemd/"
    current_images = get_current_images("/Users/oskarpawliszak/git/SRE-PYTHON/zabbix-container-switch/",["zabbix-server-mysql.container","zabbix-web-apache-mysql.container"])
    get_available_tags(current_images,["docker.io/zabbix/zabbix-server-mysql","docker.io/zabbix/zabbix-web-apache-mysql"])

if __name__ == "__main__":
    main()

