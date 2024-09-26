// Initialize empty stock list
// let stockList = ['2330.TW'];
var stockList = [];
$('#stock-list span').each(function(){
    stockList.push($(this).text());
});
console.log(stockList);
let lastStockList = [];
let lastSendList = [];
//let currentList = [];
const layout={'autosize': true, 'markers':true,
'title': {'text': ''}, 
'xaxis': {'anchor': 'y', 'domain': [0.0, 1.0], 'rangeslider': {'visible': true}}, 
'yaxis': {'anchor': 'x', 'domain': [0.0, 1.0]},
'legend': {'yanchor': 'top', 'y': 1.1, 'xanchor': 'left', 'x': 0.01, 'orientation':'h'},
'margin': {'l': 25, 'r': 5, 't': 10, 'b': 5},
}
// Cache frequently-used DOM elements
const $stockForm = $('#stock-form');
const $compSelect = $('#competition');
const $stockList = $('#stock-list');
const $submitBtn = $('#submit-btn');
const $addStockBtn = $('#addStockBtn');
const $submitPort = $('#submit-port');
const $sendPort = $('#sendPort');
const $commentPort = $('#commentPort');

// Function to add a new stock item to the list
function addStockItem(stock, text) {
    // Add item to array
    stockList.push(stock);
    // Update HTML list
    const $newItem = $(`<li class="list-group-item">
                            <span class="px-2">${text}</span> 
                            <a class="btn btn-sm btn-danger float-right delete-btn">
                                <i class="fas fa-trash-alt"></i>
                            </a>
                        </li>`);
    $stockList.append($newItem);
}
function changeFunc(value) {
    console.log(value);
    if (value === 'quadratic_utility') {
        $('#gamma').css("display", "flex");
    } else {
        $('#gamma').css("display", "none");
    }
}
// Function to delete a stock item from the list
function deleteStockItem(itemIndex) {
    // Remove item from array
    stockList.splice(itemIndex, 1);

    // Update HTML list
    $stockList.children().eq(itemIndex).remove();
}

// Event listener for delete button clicks
$stockList.on('click', '.delete-btn', function(){
    var itemIndex = $(this).closest('li').index()
    deleteStockItem(itemIndex);
    // console.log(stockList);
  });
// Event listener for submit button click
$addStockBtn.click(function(event) {
    event.preventDefault();
    // console.log($('input[name=assetSelect]').val())
    // Get selected stock from form
    var text = $('input[name=assetSelect]').val();
    // const selectedStock = text;
    // var text = $('#stock-select option:selected').text();
    // console.log(text)
    if (text !== null && text!== '' && stockList.indexOf(text)===-1) {
        // Add new item to list
        addStockItem(text, text);

        // Clear input field
        $('#stockAll').val('');
    }
    // console.log(stockList);
});

// Event listener for submit button click
$submitPort.click(function(event) {
  event.preventDefault();
  if (stockList.length < 2) {
      alert('投資組合不可小於2項');
      
  //}else if (JSON.stringify(lastSendList) == JSON.stringify(stockList)) {
   //   alert('請勿重覆建立 : 投組沒有改變');
  }else{
      $('#portModal').modal('show'); 
    //   console.log('asset confirm');
      // $(this).prop('disabled', true);
  }
});

// Event listener for submit button click
$sendPort.click(function(event) {

    if (stockList.length >= 1){
        //$('#confirmMes').replaceWith("<span>投資組合已開始建立，請等待完成訊息，或１分鐘後至分析結果區查看！</span>")
        //$('#confirmModal').modal('show'); 
        
        $submitPort.prop('disabled', true);
        $.ajax({
            url: 'http://127.0.0.1:8007/postPort', //todo create_strategy
            method: 'POST',
            data: { 
              name: $('input[name=portName]').val(),
              ts: Date(Date.now()), 
              comp: $('#competition').val(),
              lookback: $('#lookback').val(),
              frequency: $('#opt-frequency').val(),
              role: $('#role-select').val(),
              gamma: $('#util-gamma').val(),
              comment: $commentPort.val(),
              stockList: JSON.stringify(stockList)
             },
            success: function(response) {
                // console.log(response);
                // var res = JSON.parse(response);
                event.preventDefault();
                // $('#modalTitle').text('完成建立') 
                $('#sucMes').html(response);
                // <span>投資組合建立時間間隔(或與登入時間間隔)必須大於60秒</span>
                $('#confirmModal').modal('show'); 
    
                $submitPort.prop('disabled', false);
                lastSendList = stockList.map(obj => obj);
            },
            error: function(xhr) {
                console.log('Error submitting stock list: ' + xhr.responseText);
                alert('建立失敗，請確認資產名稱是否正確! 美股代號均為大寫、台股代號為數字後接".TW"或是"TWO"');
            }
        });
        $commentPort.val('');
    }
    // Get selected stock from form
});

// Event listener for submit button click
$submitBtn.click(function(event) {
    // Send stock list to server
    // console.log(event.target)
    // console.log(stockList)
    // console.log(cacheList.value, stockList);
    var texts = [];
    $('#stock-list span').each(function(){
        texts.push($(this).text());
    });
    // alert(lastStockList.includes(texts));
    if (stockList.length > 0 && JSON.stringify(lastStockList)!==JSON.stringify(stockList)) {
        // cacheList = stockList;
        $('#graph').html('<div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>')
        
        $.ajax({
            url: 'http://127.0.0.1:8007/postStock', //todo create_strategy
            method: 'POST',
            data: { stockList: JSON.stringify(stockList) },
            success: function(response) {
                $('#graph').html('')
                var graphs = JSON.parse(response);
                // console.log(graphs.data);
                Plotly.newPlot("graph", graphs.data, layout, {responsive: true});
                // console.log(response.layout);
                lastStockList = stockList.map(obj => obj);

            },
            error: function(xhr) {
                $('#graph').html('<div><span class="badge bg-warning">錯誤</span></div>')
                console.log('Error submitting stock list: ' + xhr.responseText);
            }
        });
    }
});

$(document).ready(function(){
    $("#search").on("keyup", function() {
        var value = $(this).val().toLowerCase();
        $("#stock-select option").filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });
});

$('#changeComp').click(function() {
   var competition = $('#competition').val();
   var role = $('#rrr').val();

   $.ajax({
       url: 'http://127.0.0.1:8007/result_PostStrategy',
       method: 'POST',
       data: { 
           competition: competition, 
           role: role 
       },
       success: function(response) {
           updateTable(response);
       },
       error: function(xhr) {
           alert('查詢失敗');
       }
    });
});

function updateTable(data) {
    var tbody = $('#strategyBody');
    tbody.empty(); // Clear any existing rows

    data.forEach(function(info) {
        var tr = $('<tr>');
        tr.html(`
            <th scope="col" role="alert">
                <a href="/result_view/${info[0]}" class="alert-link">
                    <span class="badge rounded-pill text-bg-info">${info[0]}</span>
                </a>
            </th>
            <td>${info[2]}</td>
            <td>${info[3]}</td>
            <td>${info[4]}</td>
            <td>${info[6]}</td>
            <td>${info[5]}</td>
            <td>${info[7]}</td>
            <td>${info[1]}</td>
        `);
        tbody.append(tr);
    });
}
