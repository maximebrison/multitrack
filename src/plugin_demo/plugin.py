from multitrack import MultitrackPlugin

app = MultitrackPlugin(
    http_port=5131,
    discovery_port=5130,
    discovery_msg="multitrack"
)

if __name__ == "__main__":
    app.run()