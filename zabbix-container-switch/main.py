import subprocess
import json
from pathlib import Path
import re
import time

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
    print("\n")
    return current_images
    


def get_available_tags(current_images,images: list[str]) -> dict[str,int]:

    current_images_tags = {}
    chosen_images = {}

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
            
            user_choice = int(input(f"Please type number of tag to update (1 - {len(newer_tags_than_running)}): ").strip())
            if user_choice > 0 and user_choice <= len(newer_tags_than_running):
                
                new_tag = sorted(newer_tags_than_running,reverse=True)[user_choice - 1]

                chosen_images.update({
                    f"{image}": new_tag
                })

        else:
            print("Newer images than running were not found.")
        print("\n")
    return chosen_images


    #Check Web

def change_images_in_prod(new_image_tags: dict[str,int],quadlets_path: str, quadlets: list[str]):
    for quadlet in quadlets:

        path = Path(quadlets_path + quadlet)
        lines = path.read_text().splitlines()

        for i,line in enumerate(lines):
        
            if line.startswith("Image="):
                running_container_image = line.split("=")[1].split(":")[0]
                running_image_tag = line.split("=")[1].split(":")[1]
                new_container_image = f"{running_container_image}:ubuntu-7.0.{new_image_tags[running_container_image]}"
                pull_container_image_command = f"podman pull {new_container_image}"
                lines[i] = f"Image={new_container_image}"
                print(f"Updating {running_container_image} {running_image_tag} -> {new_container_image}")

                subprocess.run(pull_container_image_command.split())
        
        path.write_text("\n".join(lines) + "\n")

    stop_web_apache_mysql_command = "systemctl stop --user zabbix-web-apache-mysql.service"
    stop_server_mysql_command = "systemctl stop --user zabbix-server-mysql.service"
    daemon_reload_command = "systemctl daemon-reload --user"
    start_web_apache_mysql_command = "systemctl start --user zabbix-web-apache-mysql.service"
    start_server_mysql_command = "systemctl start --user zabbix-server-mysql.service"

    print("Stopping web apache container...")
    subprocess.run(stop_web_apache_mysql_command.split())
    print("Stopping server container...")

    subprocess.run(stop_server_mysql_command.split())
    print("Reloading daemon...")
    subprocess.run(daemon_reload_command .split())
    time.sleep(3)
    print("Starting server...")
    subprocess.run(start_server_mysql_command.split())
    time.sleep(10)
    print("Starting web apache...")
    subprocess.run(start_web_apache_mysql_command.split())
    time.sleep(10)

    subprocess.run(["podman","ps"])

                

def main():
    quadlets_path = "/home/zabbix-runner/.config/containers/systemd/"
    quadlets = ["zabbix-server-mysql.container","zabbix-web-apache-mysql.container"]

    current_images = get_current_images(quadlets_path, quadlets)
    chosen_images = get_available_tags(current_images,["docker.io/zabbix/zabbix-server-mysql","docker.io/zabbix/zabbix-web-apache-mysql"])
    change_images_in_prod(chosen_images,quadlets_path,quadlets)
if __name__ == "__main__":
    main()