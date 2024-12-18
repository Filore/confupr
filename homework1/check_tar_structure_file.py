import tarfile

tar_path = '/Users/matvej/PycharmProjects/dz1/test_vfs.tar'  #

with tarfile.open(tar_path, 'r') as tar:
    for member in tar.getmembers():
        print(member.name)