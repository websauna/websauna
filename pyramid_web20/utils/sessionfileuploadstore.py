

class SessionFileUploadTempStore(object):
    def __init__(self, request):
        try:
            self.tempdir=request.registry.settings['pyramid_deform.tempdir']
        except KeyError:
            raise ConfigurationError(
                'To use SessionFileUploadTempStore, you must set a  '
                '"pyramid_deform.tempdir" key in your .ini settings. It '
                'points to a directory which will temporarily '
                'hold uploaded files when form validation fails.')
        self.request = request
        self.session = request.session
        self.tempstore = self.session.setdefault('substanced.tempstore', {})

    def preview_url(self, uid):
        return None

    def __contains__(self, name):
        return name in self.tempstore

    def __setitem__(self, name, data):
        newdata = data.copy()
        stream = newdata.pop('fp', None)

        if stream is not None:
            while True:
                randid = binascii.hexlify(os.urandom(20))
                if not isinstance(randid, string_types):
                    randid = randid.decode("ascii")
                fn = os.path.join(self.tempdir, randid)
                if not os.path.exists(fn):
                    # XXX race condition
                    fp = open(fn, 'w+b')
                    newdata['randid'] = randid
                    break
            for chunk in chunks(stream):
                fp.write(chunk)

        self.tempstore[name] = newdata
        self.session.changed()

    def get(self, name, default=None):
        data = self.tempstore.get(name)

        if data is None:
            return default

        newdata = data.copy()

        randid = newdata.get('randid')

        if randid is not None:

            fn = os.path.join(self.tempdir, randid)
            try:
                newdata['fp'] = open(fn, 'rb')
            except IOError:
                pass

        return newdata

    def __getitem__(self, name):
        data = self.get(name, _marker)
        if data is _marker:
            raise KeyError(name)
        return data

def chunks(stream, chunk_size=10000):
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        yield chunk
