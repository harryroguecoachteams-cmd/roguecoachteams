/**
 * Rogue Coach Teams: contact form lead sink (Google Apps Script)
 *
 * WHY THIS FILE EXISTS
 * The existing "RCT payments log" web app answers GET but has no doPost, so a
 * POST to it returns HTTP 405 and the contact form has nowhere to send a lead.
 * Until this is deployed, the form on contact.html composes the whole enquiry
 * and opens the visitor's mail client instead, so no lead is ever lost.
 *
 * TO TURN THE FORM INTO A SILENT SEND
 *   1. Open the Apps Script project bound to the sheet you want leads in
 *      (or File > New > Apps Script and set SHEET_ID below).
 *   2. Paste this file in. Keep any existing doGet; only doPost is added.
 *   3. Deploy > New deployment > Web app
 *        Execute as:        Me
 *        Who has access:    Anyone
 *   4. Copy the /exec URL.
 *   5. In assets/js/site.js set:
 *        var LEAD_ENDPOINT = "https://script.google.com/macros/s/…/exec";
 *   6. Submit the form once and confirm a row appears.
 *
 * NOTE ON CORS: Apps Script does not send CORS headers, so the site posts with
 * mode:"no-cors" and cannot read the response. That is fine: the write still
 * happens. It also means the browser sends Content-Type: text/plain, which is
 * why the body is parsed out of e.postData.contents rather than e.parameter.
 */

// Leave blank to use the sheet this script is bound to.
var SHEET_ID = '';
var TAB_NAME = 'Leads';
var NOTIFY = 'roguecoachteams@gmail.com';   // set to '' to switch the email off

var HEADERS = ['Timestamp', 'Name', 'Email', 'Interested in', 'Message', 'Source'];

function doPost(e) {
  try {
    var data = {};
    if (e && e.postData && e.postData.contents) {
      try {
        data = JSON.parse(e.postData.contents);
      } catch (err) {
        data = e.parameter || {};
      }
    } else if (e) {
      data = e.parameter || {};
    }

    var sheet = getSheet_();
    sheet.appendRow([
      new Date(),
      data.name || '',
      data.email || '',
      data.goal || '',
      data.message || '',
      data.source || ''
    ]);

    if (NOTIFY) {
      MailApp.sendEmail({
        to: NOTIFY,
        subject: 'New website enquiry from ' + (data.name || 'unknown'),
        replyTo: data.email || NOTIFY,
        body: [
          'Name:  ' + (data.name || ''),
          'Email: ' + (data.email || ''),
          'Wants: ' + (data.goal || ''),
          '',
          data.message || '',
          '',
          'Sent from ' + (data.source || 'the website')
        ].join('\n')
      });
    }

    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}

function getSheet_() {
  var book = SHEET_ID ? SpreadsheetApp.openById(SHEET_ID)
                      : SpreadsheetApp.getActiveSpreadsheet();
  var sheet = book.getSheetByName(TAB_NAME);
  if (!sheet) {
    sheet = book.insertSheet(TAB_NAME);
    sheet.appendRow(HEADERS);
    sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function json_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/** Run this from the editor once to confirm the sheet and email both work. */
function selfTest() {
  var res = doPost({
    postData: {
      contents: JSON.stringify({
        name: 'Self test',
        email: NOTIFY,
        goal: 'Testing',
        message: 'If you can see this row, the endpoint works. Delete it.',
        source: 'selfTest()'
      })
    }
  });
  Logger.log(res.getContent());
}
