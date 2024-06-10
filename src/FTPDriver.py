import ftplib


class FTPDriver:
    def __init__(self, host: str, port: int, username: str, password: str) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.connect()
        self.ftp.cwd("captures")

    def connect(self) -> None:
        self.ftp = ftplib.FTP()
        self.ftp.connect(self.host, self.port)
        self.ftp.login(self.username, self.password)

    def upload(self, file_path: str) -> None:
        with open(file_path, "rb") as file:
            self.ftp.storbinary(f"STOR {file_path}", file)

    def download(self, file_path: str) -> None:
        with open(file_path, "wb") as file:
            self.ftp.retrbinary(f"RETR {file_path}", file.write)

    def list_files(self) -> list[str]:
        return self.ftp.nlst("-a")

    # Get the latest image full link from the captures directory
    def get_latest_image(self) -> str:
        files = self.ftp.nlst("-t")
        return "ftp://" + self.username + ":" + self.password + "@" + self.host + "/captures/" + files[0]

    def close(self) -> None:
        self.ftp.quit()
