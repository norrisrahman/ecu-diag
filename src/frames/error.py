import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from .base import HondaECU_AppPanel
from pydispatch import dispatcher
from eculib.honda import DTC

class ErrorListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
	def __init__(self, parent, ID, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		ListCtrlAutoWidthMixin.__init__(self)
		self.setResizeColumn(2)

class HondaECU_ErrorPanel(HondaECU_AppPanel):

	def Build(self):
		self.SetMinSize((400,250))
		self.errorp = wx.Panel(self)

		self.errorlist = ErrorListCtrl(self.errorp, wx.ID_ANY, style=wx.LC_REPORT|wx.LC_HRULES)
		self.errorlist.InsertColumn(1,"DTC",format=wx.LIST_FORMAT_CENTER,width=50)
		self.errorlist.InsertColumn(2,"Description",format=wx.LIST_FORMAT_CENTER,width=-1)
		self.errorlist.InsertColumn(3,"Current",format=wx.LIST_FORMAT_CENTER,width=80)
		self.errorlist.InsertColumn(4,"Past",format=wx.LIST_FORMAT_CENTER,width=80)

		self.resetbutton = wx.Button(self.errorp, label="Clear Codes")
		self.resetbutton.Disable()

		self.errorsizer = wx.BoxSizer(wx.VERTICAL)
		self.errorsizer.Add(self.errorlist, 1, flag=wx.EXPAND|wx.ALL, border=10)
		self.errorsizer.Add(self.resetbutton, 0, flag=wx.ALIGN_RIGHT|wx.BOTTOM|wx.RIGHT, border=10)
		self.errorp.SetSizer(self.errorsizer)

		# if "dtccount" in self.parent.ecuinfo and self.parent.ecuinfo["dtccount"] > 0:
		# 	self.resetbutton.Enable(True)
		# if "dtc" in self.parent.ecuinfo:
		# 	for code in self.parent.ecuinfo["dtc"][hex(0x74)]:
		# 		self.errorlist.Append([code, DTC[code] if code in DTC else "Unknown", "current"])
		# 	for code in self.parent.ecuinfo["dtc"][hex(0x73)]:
		# 		self.errorlist.Append([code, DTC[code] if code in DTC else "Unknown", "past"])

		self.mainsizer = wx.BoxSizer(wx.VERTICAL)
		self.mainsizer.Add(self.errorp, 1, wx.EXPAND)
		self.SetSizer(self.mainsizer)
		self.Fit()
		self.Layout()
		# self.mainsizer.Fit(self)

		self.Bind(wx.EVT_BUTTON, self.OnClearCodes)

		wx.CallAfter(dispatcher.send, signal="ErrorPanel", sender=self, action="dtc.on")

	def OnClose(self, event):
		wx.CallAfter(dispatcher.send, signal="ErrorPanel", sender=self, action="dtc.off")
		HondaECU_AppPanel.OnClose(self, event)

	def OnClearCodes(self, event):
		self.resetbutton.Disable()
		self.errorlist.DeleteAllItems()
		wx.CallAfter(dispatcher.send, signal="ErrorPanel", sender=self, action="dtc.clear")

	def KlineWorkerHandler(self, info, value):
		if info == "dtccount":
			if value > 0:
				self.resetbutton.Enable(True)
			else:
				self.resetbutton.Enable(False)
				self.errorlist.DeleteAllItems()
		elif info == "dtc":
			self.errorlist.DeleteAllItems()
			codes = {}
			for code in value[hex(0x74)]:
				if code not in codes:
					codes[code] = [DTC[code],False,False]
				codes[code][1] = True
			for code in value[hex(0x73)]:
				if code not in codes:
					codes[code] = [DTC[code],False,False]
				codes[code][2] = True
			for k,v in codes.items():
				self.errorlist.Append([k, v[0], "X" if v[1] else "", "X" if v[2] else ""])
			self.Layout()
