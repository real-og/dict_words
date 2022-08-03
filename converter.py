def create_url(input):
    if (input[:14] == 'https://genius') and (input.find(' ') == -1):
        return input
    
    url = 'https://genius.com/'
    for word in input.capitalize().split(' '):
        url = url + word + '-'
    return url + 'lyrics'