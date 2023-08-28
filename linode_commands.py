def get_list_command(cluster):
    list_command = [
        "linode-cli", "obj", "la",
        "--cluster", cluster,
    ]
    return list_command


def get_download_command(cluster, bucket, file_name):
    download_command = [
        "linode-cli", "obj", "get",
        "--cluster", cluster,
        bucket,
        file_name,
    ]
    return download_command


def get_remove_command(cluster, bucket, file_name):
    remove_command = [
        "linode-cli", "obj", "rm",
        "--cluster", cluster,
        bucket,
        file_name,
    ]
    return remove_command