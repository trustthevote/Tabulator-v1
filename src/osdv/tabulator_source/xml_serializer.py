def xml_serialize(dict_, indent):
    """
    Serialize into xml a hierarchical data structure consisting of
    dictionaries and lists of dictionaries, using recursion.
    """

    result = []
    spaces = ''
    for i in range(indent):
        spaces = '%s ' % spaces
    keys_ = dict_.keys()
    keys_.sort()
    for key in keys_:
        if isinstance(dict_[key], dict):
            result.append( '%s<%s>\n' % (spaces, key) )
            result += xml_serialize(dict_[key], indent + 2)
            result.append( '%s</%s>\n' % (spaces, key) )
        elif isinstance(dict_[key], list):
            result.append( '%s<%s>\n' % (spaces, key) )
            for element in dict_[key]:
                result += xml_serialize(element, indent + 2)
            result.append( '%s</%s>\n' % (spaces, key) )
        else:
            s = '<%s>%s</%s>' % (key, str(dict_[key]), key)
            if 'party_id' in keys_:
                if key == keys_[0]:
                    result.append( '%s%s ' % (spaces, s) )
                elif key == keys_[len(keys_) - 1]:
                    result.append( '%s\n' % s )
                else:
                    result.append( '%s ' % s )
            else:
                result.append( '%s%s\n' % (spaces, s) )
    if indent == 0:
        print result
    return result
