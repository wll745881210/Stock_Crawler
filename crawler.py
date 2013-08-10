#!/usr/bin/python

import wx
from ConfigParser import ConfigParser
from main_frame import GladeFrame
from backend import crawler_table
import threading

class backend_thread(threading.Thread):
    def __init__(self,crawler):
        self.crawler = crawler;
        threading.Thread.__init__(self, name = 'crawler_backend' );
    #
        
    def run(self):
        self.crawler.get_all_data();
    #

    def terminate(self):
        self.raise_exc(SystemExit);
#        

class my_frame(GladeFrame):

    def __init__(self, *args, **kwds):
        GladeFrame.__init__(self, *args, **kwds);
        self.__stock_id_name    = 'stock_id.txt';
        self.__item_list_name   = 'item_list.ini';
        self.__set_binding();
        self.__set_extra_init();
        self.crawler            = crawler_table(  );
    #
    
    def __set_binding(self):
        self.Bind(wx.EVT_BUTTON, self.__save_button_click, self.save_button);
        self.Bind(wx.EVT_BUTTON, self.__run_button_click,  self.run_button);
        self.Bind(wx.EVT_CLOSE,  self.__close_frame);

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__list_sel, self.stat_item_list );
        self.Bind(wx.EVT_BUTTON, self.__del_button_click,  self.del_button);
        self.Bind(wx.EVT_BUTTON, self.__add_button_click,  self.add_button);

    def __set_extra_init(self):
        self.stat_item_list.InsertColumn( 0, 'Item', width=80 );
        self.stat_item_list.InsertColumn( 1, 'Example URL', width=250 );
        self.__stock_id_ls('load');
        self.__stat_item_ls('load');
    #

    def __on_exit(self):
        self.__stock_id_ls('save');
        self.__stat_item_ls('save');
        try:
            self.pd.Destroy();
        except:
            print "Exit.";
    #

    def __stock_id_ls(self,flag):
        if flag == 'load':
            stock_id_fio = open( self.__stock_id_name, 'r' );
            stock_id_content = stock_id_fio.read();
            self.stock_id_ctrl.SetValue( stock_id_content );
        elif flag == 'save':
            stock_id_fio = open( self.__stock_id_name, 'w' );
            stock_id_content = self.stock_id_ctrl.GetValue();
            stock_id_fio.write( stock_id_content );
        #
        stock_id_fio.close();
        return;
    #

    def __stat_item_ls(self,flag):
        cp  = ConfigParser(  );
        self.sec = 'statistics_items';
        if flag == 'load':
            cp.read( self.__item_list_name );
            self.sec = cp.sections()[0];
            for opt in cp.options( self.sec ):
                val = cp.get( self.sec, opt );
                idx = self.stat_item_list.InsertStringItem( 0, opt.decode('utf8') );
                self.stat_item_list.SetStringItem( idx, 1, val );
            #
        elif flag == 'save':
            cp.add_section( self.sec );
            for i in range(self.stat_item_list.GetItemCount()):
                opt = self.stat_item_list.GetItem( i, col=0 ).Text.encode('utf8');
                if opt == '':
                    continue;
                val = self.stat_item_list.GetItem( i, col=1 ).Text.encode('utf8');
                cp.set( self.sec, opt, val );
            #
            cp.write( open(self.__item_list_name, 'w' ) );
        #

    def __save_button_click(self,event):
        self.__stock_id_ls('save');
        self.__stat_item_ls('save');
    #

    def __run_button_click(self,event):
        self.__save_button_click(event);
        self.crawler.set_stock_id_item( self.__item_list_name, self.__stock_id_name );

        fd = wx.DirDialog(self,"Specify Output Path",style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON);
        fd_res = fd.ShowModal();
        if fd_res == wx.ID_OK:
            output_dir = fd.GetPath();
            self.crawler.output_dir = output_dir;
            fd.Destroy();
        elif fd_res == wx.ID_CANCEL:
            fd.Destroy();
            return;

        progress_max = self.crawler.tot_fetch_num;
        pd = wx.ProgressDialog("Fetching Progress", "Time Elapsed/Remaining", progress_max,\
                                style= wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME);
        try:
            self.backend = backend_thread(self.crawler);
            self.backend.setDaemon(True);
            self.backend.start();
        
            while self.crawler.tot_fetch_count < progress_max:
                wx.Sleep(0.5);
                pd.Update(self.crawler.tot_fetch_count);
        #
        finally:
            pd.Destroy();
    #

    def __list_sel(self,event):
        self.__list_sel_idx = event.GetIndex();
    #

    def __del_button_click(self,event):
        self.stat_item_list.DeleteItem(self.__list_sel_idx);
    #

    def __add_button_click(self,event):
        self.stat_item_list.InsertStringItem( 0, '' );
    #        

    def __close_frame(self,event):
        dlg = wx.MessageDialog(self, \
            "Save all changes to the stock IDs and statistics items?", \
            "Confirm Exit", wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION);
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_YES:
            self.__stock_id_ls('save');
        if result != wx.ID_CANCEL:
            self.Destroy();
    #
#

class crawler_window(wx.App):

    def OnInit(self):
        wx.InitAllImageHandlers()
        mf = my_frame(None, -1, "")
        self.SetTopWindow(mf)
        mf.Show()
        return 1;
    #

if __name__=='__main__':
    stock_crawler = crawler_window(0)
    stock_crawler.MainLoop()
#

