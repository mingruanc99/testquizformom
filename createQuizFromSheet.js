function createQuizFromSheet() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var rows = sheet.getDataRange().getValues();
  var form = FormApp.create('Quiz Tổng Hợp - ' + new Date().toLocaleDateString());
  form.setIsQuiz(true);

  for (var i = 1; i < rows.length; i++) {
    var row = rows[i];
    var questionTitle = row[0] ? row[0].toString().trim() : "";
    
    // Bỏ qua nếu dòng này không có câu hỏi (dòng trống)
    if (!questionTitle || questionTitle === "") continue;

    var rawChoices = [row[1], row[2], row[3], row[4]];
    var correctLetter = row[5] ? row[5].toString().toUpperCase().trim() : "A";
    var letterMap = {"A": 0, "B": 1, "C": 2, "D": 3};
    var correctIdx = letterMap[correctLetter] || 0;

    var item = form.addMultipleChoiceItem();
    item.setTitle(questionTitle);
    
    var choicesArray = [];
    var seenText = {}; // Dùng để check trùng lặp

    for (var j = 0; j < rawChoices.length; j++) {
      var choiceText = rawChoices[j] ? rawChoices[j].toString().trim() : "";
      
      // CHỈ thêm nếu đáp án KHÔNG trống và KHÔNG bị trùng nội dung
      if (choiceText !== "" && !seenText[choiceText]) {
        var isCorrect = (j === correctIdx);
        choicesArray.push(item.createChoice(choiceText, isCorrect));
        seenText[choiceText] = true;
      }
    }

    // Nếu sau khi lọc mà không còn đáp án nào thì xóa câu hỏi này đi
    if (choicesArray.length > 0) {
      item.setChoices(choicesArray);
      item.setPoints(1);
    } else {
      // Xóa item nếu nó là dòng tiêu đề chuyên đề hoặc dòng lỗi
      form.deleteItem(item);
    }
  }
  
  Logger.log('Đã sửa xong lỗi duplicate! Link: ' + form.getEditUrl());
}