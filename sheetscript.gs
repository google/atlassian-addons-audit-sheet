/* Copyright 2018 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

function onOpen() {
    var alert = 'Please do NOT edit any columns except for Tag or Notes. Plugin data gets updated by script. (See note in cell A1)';
    SpreadsheetApp.getActiveSpreadsheet().toast(alert,"NOTICE",-1);
}

function sendEmails() {
  
  var emailAddress = "YOUREMAILADDRESS"; 
  var daysprior = 7 ;
  
  var today = new Date().toLocaleDateString();  // Today's date, without time
  var datecheck = new Date(Date.now() + daysprior *(24*3600*1000)).toLocaleDateString();  //
  Logger.log("CHECKING = " + datecheck);
  
  var sheets = SpreadsheetApp.getActiveSpreadsheet().getSheets();
  
  for (var j = 0; j < sheets.length; j++) {
     Logger.log("SHEETS = " + sheets.length);
    
     var sheet = sheets[j];
     var sheetname = sheet.getSheetName();
     
     var sheeturl = '';
     sheeturl += SpreadsheetApp.getActiveSpreadsheet().getUrl();
     sheeturl += '#gid=';
     sheeturl += sheet.getSheetId();
    
     var startRow = 2;  // First row of data to process
     var numRows = sheet.getLastRow()-1;

     Logger.log("SHEETNAME = " + sheetname);
     Logger.log("ROWS = " + numRows);
     // Fetch the range of cells A2:B999
     var dataRange = sheet.getRange(startRow, 1, numRows, 26)
     // Fetch values for each row in the Range.
     var data = dataRange.getValues();
     for (var i = 0; i < data.length; ++i) {
        var row = data[i];
        var plugin = row[0];     // First column
        var realrow = Number(i+2);
        var pluginNote = sheet.getRange(realrow,1).getNote();
       
        Logger.log("REALROW = " + realrow);
        Logger.log("PLUGIN = " + plugin);
        Logger.log("NOTE = " + pluginNote);
       
        if (plugin != "" && !pluginNote.match(/Disabled/) ) {
            var expiring = row[6]; 
 
            Logger.log("EXPIRING = " + expiring);
       
            var expireDate = "";    
            if (expiring != "N/A") {
               expireDate = expiring.toLocaleDateString();  // date specified in cell F
            }

          var subject = sheetname + " Plugin expiring in " + daysprior + " days: " + plugin + " on " + expireDate;
          var message = sheetname + " Plugin expiring in " + daysprior + " days: " + plugin;
          message += "\nExpires on: " + expireDate;
          message += "\n\nDetails here: " + sheeturl;
      
            if (expireDate == datecheck) {     // Send email if X days out
              
               MailApp.sendEmail(emailAddress, subject, message);  
               Logger.log("MAIL = " + subject);
      
         // Make sure the cell is updated right away in case the script is interrupted
               SpreadsheetApp.flush();
            }
         }
      }
   }
}
