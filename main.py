import os
import requests


class PullRequest:

    def __init__(self):
        self.repository_path = "https://api.github.com/repos/go-gitea/gitea/releases/latest"
        self.latest_release = None
        self.last_saved = None
        self.sha1sum = None
        self.sha256sum = None
        self.md5sum = None

    def get_latest(self):
        self.latest_release = requests.get(f"{self.repository_path}").json()["name"]
        return self.latest_release

    def read_file(self):
        get_saved = [line.split() for line in open(".version", "r+")]
        self.last_saved = get_saved[0][0]
        return self.last_saved

    def write_file(self, latest_release):
        file = open(".version", "r+")
        file.seek(0)
        file.truncate()
        print(latest_release, file=file)

    def git_pull_and_checkout(self):
        if os.path.isdir("spksrc"):
            print("DEBUG : Repo already exists.")
            pass
        else:
            print("DEBUG : Repo does not exist. Setting up...")
            os.popen(f"git clone https://github.com/Wuszek/spksrc.git && cd spksrc && git remote add "
                     f"upstream https://github.com/SynoCommunity/spksrc.git").read()

        # TODO : Uncommented is for testing purposes
        # os.popen(f"cd spksrc && git pull upstream master && git rebase upstream/master && git checkout -b"
        #          f" {self.latest_release}").read()
        os.popen(f"cd spksrc && git pull upstream master && git rebase upstream/master").read()

    def create_digest(self, hash_type):
        digest = os.popen(f"{hash_type.lower()} {self.latest_release}.tar.gz").read()
        temp = digest.split()
        temp.reverse()
        temp[0] = f"gitea-{self.latest_release}.tar.gz"
        temp.insert(1, hash_type[:-3])
        return " ".join(temp)

    def download_gitea_package(self):
        if os.path.isfile(f"{self.latest_release}.tar.gz"):
            print(f"TESTING : File {self.latest_release}.tar.gz is already there.")
            pass
        else:
            print(f"DEBUG : Downloading package.")
            os.popen(f"wget https://github.com/go-gitea/gitea/archive/refs/tags/{self.latest_release}.tar.gz").read()
        try:
            self.sha1sum = self.create_digest("SHA1SUM")
            self.sha256sum = self.create_digest("SHA256SUM")
            self.md5sum = self.create_digest("MD5SUM")
            print("DEBUG : Calculating checksums... DONE.")
        except Exception as e:
            print("ERROR: Getting checksums went wrong.")
            exit(1)

    def update_digest_file(self):
        try:
            file = open("digest", "r+")
            file.seek(0)
            file.truncate()
            file.write(f"{self.sha1sum}\n{self.sha256sum}\n{self.md5sum}\n")
            file.close()
            print("Updated Digest successfully.")
        except Exception as e:
            print("Something went wrong during digest file update.")

    def update_cross_makefile(self):
        if os.path.isfile("Makefile"):
            with open("Makefile", "r+") as file:
                data = file.readlines()
            data[1] = f"PKG_VERS = {self.latest_release[1:]}\n"
            with open("Makefile", "r+") as file:
                file.writelines(data)
            file.close()
            print("DEBUG : Updated Makefile successfully.")
        else:
            print("ERROR : Something went wrong during Makefile file update.")
            exit(1)

    def run(self):
        # TODO: check if digest file exist
        # TODO: check if Makefile exist = just check if repo is there and if is updated
        if self.get_latest() != self.read_file():
            print("DEBUG : Newer version appeared: " + self.latest_release)
            self.write_file(self.latest_release)
        else:
            print(f"DEBUG : No changes. Still {self.last_saved} is newest.")

        self.git_pull_and_checkout()
        self.download_gitea_package()
        #self.update_digest_file()
        #self.update_cross_makefile()


gitea_update = PullRequest()
gitea_update.run()
