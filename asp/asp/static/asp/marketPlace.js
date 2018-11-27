$(document).ready(function() {
    var sumWeight = 0;
    $('.itemQuantity').each(function() {
        var quantity = parseInt($(this).val(), 10);
        if (!quantity)
            quantity = 0;
        sumWeight += quantity * parseFloat($(this).closest('div').find('.itemWeight').val(), 10);
    });
    var roundedWeight = Number(Math.round(sumWeight + 'e2') + 'e-2');
    $('#sumWeight').html(roundedWeight);
});

$('body').on('keyup click', '.itemQuantity', function() {
    if (parseInt($(this).val()) < 0) {
        $(this).val(0);
    }
    var sumWeight = 0;
    $('.itemQuantity').each(function() {
        var quantity = parseInt($(this).val(), 10);
        if (!quantity)
            quantity = 0;
        sumWeight += quantity * parseFloat($(this).closest('div').find('.itemWeight').val(), 10);
    });
    if (sumWeight > 23.8) {
        $('#placeOrder').prop('disabled', true);
    }
    else {
        $('#placeOrder').prop('disabled', false);
    }
    var roundedWeight = Number(Math.round(sumWeight + 'e2') + 'e-2');
    $('#sumWeight').html(roundedWeight);
});