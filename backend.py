#!/usr/bin/python

import urllib2
from BeautifulSoup import *
import time
import re
from ConfigParser import ConfigParser
import xlwt

class crawler_table:

    def __init__( self ):
        self.__date_pat  = re.compile( '\d{4}-\d{2}-\d{2}' );
        self.__stock_id_pat = re.compile( '\d{6}' );
        self.__sheet_map = {  };
        self.tot_fetch_count = 0.;
        self.output_dir = '';
    #

    def __fetch_sheet_single( self, item, stock_id ):
        url = self.__sheet_map[ item ];
        url = url.replace( 'STOCK_ID', str( stock_id ) );
        try:
            sheet_content = urllib2.urlopen( url );
        except:
            return;
        soup       = BeautifulSoup( sheet_content );
        table_html = soup.find( 'table', id='Table1' );
        rows       = table_html.findAll('tr');
        date       = [];
        val        = [];
        
        for tr in rows:
            cols = tr.findAll('td');
            for td in cols:
                text = td.find( text = True ).replace( ',', '' );
                if self.__date_pat.search( text ):
                    date.append( time.mktime( time.strptime( text, '%Y-%m-%d' ) ) );
                else:
                    try:
                        val.append( float( text ) );
                    except:
                        val.append( float('nan') );
                    break;
        #
        self.tot_fetch_count += 1.;
        print "Progress: %.0f per cent" % (self.tot_fetch_count/self.tot_fetch_num*100.);
        return (date, val);
    #

    def __fetch_sheet( self, stock_id ):
        self.res_map = {};

        for opt in self.__sheet_map:
            self.res_map[ opt ] = self.__fetch_sheet_single( opt, stock_id );
        #
    #

    def __write_to_excel( self, stock_id ):
        xls_name =  str(stock_id) + '.xls';
        if self.output_dir != '':
            xls_name = self.output_dir + '/' + xls_name;

        xls = xlwt.Workbook();
        for item in self.item_list:
            data = self.res_map[ item ]; 
            sheet = xls.add_sheet( item.decode('utf8') );
            sheet.write( 0, 0, 'Date'.decode('utf8') );
            sheet.write( 0, 1, item.decode('utf8') );
            for j, date in enumerate(data[0]):
                val        = data[1][j];
                local_date = time.localtime( date );
                date_str   = time.strftime('%y-%m', local_date);
                sheet.write( j + 1, 0, date_str.decode('utf8') );
                if ( val > 1000. ) | ( val < -1000. ):
                    style = xlwt.easyxf(num_format_str='#,##0');
                else:
                    style = xlwt.easyxf(num_format_str='#,##0.00');
                sheet.write( j + 1, 1, val, style );
            #
        xls.save( xls_name );
        #
    
    def set_stock_id_item( self, item_list_name, stock_id_file ):
        cp = ConfigParser(  );
        cp.read( item_list_name );
        sec = cp.sections()[0];
        self.item_list=[];

        for opt in cp.options( sec ):
            val = cp.get( sec, opt );
            if ( val != '' ) & ( opt != '' ) :
                val, num = re.subn( self.__stock_id_pat, 'STOCK_ID', val );
                self.__sheet_map[ opt ] = val;
                self.item_list.append( opt );
        #
        fin = open( stock_id_file );
        self.stock_id_arr = fin.readlines();
        for stock_id in self.stock_id_arr:
            try:
                temp_id = int(stock_id);
            except:
                self.stock_id_arr.remove( stock_id );
        #
        self.tot_fetch_num = len( self.stock_id_arr ) * len( self.__sheet_map );
    #

    def get_all_data( self ):        
        for stock_id in self.stock_id_arr:
            stock_id = stock_id.replace('\n','');
            self.__fetch_sheet( stock_id );
            self.__write_to_excel( stock_id );
        self.tot_fetch_count = 0;
    #
#

if __name__=='__main__':
    test = crawler_table(  );
    test.set_stock_id_item( 'item_list.ini', 'stock_id.txt' )
    test.get_all_data(  );
#

