from tests import FlexGetBase
from nose.plugins.attrib import attr


class TestJdownloader(FlexGetBase):
    __yaml__ = """
            tasks:
              test0:
                mock:
                  - {title: 'foobar0', url: 'http://mantolama.be/wp-content/uploads/yootheme/widgetkit/gallery/showcase1/image3.jpg'}
                jdownloader: yes
                accept_all: yes
                disable: builtins
              test1:
                mock:
                  - {title: 'foobar1', url: 'http://mantolama.be/wp-content/uploads/yootheme/widgetkit/gallery/showcase1/image4.jpg'}
                jdownloader:
                  api-mode: cnl
                  api: http://127.0.0.1:9666/flash
                accept_all: yes
                disable: builtins
              test2:
                mock:
                  - {title: 'foobar2', url: 'http://mantolama.be/wp-content/uploads/yootheme/widgetkit/gallery/showcase1/image5.jpg'}
                jdownloader:
                  api-mode: cnl
                  api: http://127.0.0.1:9666/flash
                  runcmd: c:\Users\%USERNAME%\JDownloader1\JDownloader.exe
                accept_all: yes
                disable: builtins
              test3:
                mock:
                  - {title: 'foobar3', url: 'http://mantolama.be/wp-content/uploads/yootheme/widgetkit/gallery/showcase1/image6.jpg'}
                jdownloader:
                   api-mode: remotecontrol
                   api: http://127.0.0.1:10025
                   grabber: false
                   start: true
                   runcmd: c:\Users\%USERNAME%\JDownloader1\JDownloader.exe
                accept_all: yes
                disable: builtins
        """


    @attr(online=True)
    def test_flashgot(self):
        # run the feed
        self.execute_task('test0')
        assert self.task.entries, 'no entries created / site may be down'

    @attr(online=True)
    def test_cnl(self):
        # run the feed
        self.execute_task('test1')
        assert self.task.entries, 'no entries created / site may be down'
        self.execute_task('test2')
        assert self.task.entries, 'no entries created / site may be down'

    @attr(online=True)
    def test_remotecontrol(self):
        # run the feed
        self.execute_task('test3')
        assert self.task.entries, 'no entries created / site may be down'
