def make_path_chunk(chunk):
    if chunk == '':
        return chunk
    # if chunk[0] != '/':
    #     chunk = ''.join(['/', chunk])
    # while chunk[0:2] == '//':
    #     chunk = chunk[1:]
    chunk = chunk.lstrip('/')
    chunk = ''.join(['/', chunk])
    chunk = chunk.rstrip('/')
    return chunk
