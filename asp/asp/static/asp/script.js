console.log('im here')

$('body').on('keyup', '.orderQuantity', function() {
    $(this).attr('id');
    $('#placeOrder').prop('disabled', true);
    var sumWeight;
    $('.orderQuantity').each(function() {
        sumWeight += $(this).val() * $('.' + $(this).attr('id'));
    });
    console.log(sumWeight);
});
