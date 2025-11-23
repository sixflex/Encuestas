$(document).ready(function () {

    function handleSearch() {
        var searchText = $('#searchInput').val().toLowerCase();


        $('table tbody tr').hide();


        $('table tbody tr').each(function () {
            var rowText = $(this).text().toLowerCase();
            if (rowText.includes(searchText)) {
                $(this).show();
            }
        });
    }


    $('#searchInput').on('input', function () {
        handleSearch();
    });


    $('#searchIcon').on('click', function () {
        handleSearch();
    });
});