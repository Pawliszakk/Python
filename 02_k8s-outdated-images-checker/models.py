class Entry:
    def __init__(self, pod, namespace, container, image, image_latest=None, status=None):
        self.pod = pod
        self.namespace = namespace
        self.container = container
        self.image = image
        self.image_latest = image_latest
        self.status = status