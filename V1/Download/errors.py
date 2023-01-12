# class DownloadFailed(Exception):
# 	def __init__(self, message, *args):
# 		super(DownloadFailed, self).__init__(message, *args)
#
# 		self.args = (message, *args)
#
# 	def __str__(self):
# 		return str(self.args[0])

class FileSystemError(Exception):
	def __init__(self, message, *args):
		super(FileSystemError, self).__init__(message, *args)

		self.args = (message, *args)

	def __str__(self):
		return str(self.args[0])

class FolderNotFoundError(FileSystemError): pass
class PathIsFileError(FileSystemError): pass