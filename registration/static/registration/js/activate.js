
function mostrarModal(elemento) {

    var elementId = $(elemento).data('element-id');

    $('#myModal').data('element-id', elementId);

    $('#myModal').modal('show');

    var blockUrl = baseUrl.replace('0', elementId.toString());
    console.log('URL de bloqueo al hacer clic:', blockUrl);
    $('#blockButton').attr('href', blockUrl);
}

$(document).ready(function () {
    $('#myModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var elementId = button.data('element-id');
        var modal = $(this);


        if (elementId !== undefined) {

            var blockUrl = baseUrl.replace('0', elementId.toString());
            console.log('URL de bloqueo al hacer clic:', blockUrl);
            modal.find('#blockButton').attr('href', blockUrl);
        }
    });
});