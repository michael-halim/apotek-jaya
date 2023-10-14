$(function () {
    $('[class*="dropdown-child-"]').hide();
    $('body').on('click','.dropdown-parent',function(){
        var id = $(this).attr('id');
        $('.dropdown-child-' + id).slideToggle('fast');
        
        if ($(this).find('div.icon-dropdown > i').hasClass('fa-caret-up')){
            $(this).find('div.icon-dropdown > i').removeClass('fa-caret-up');
            $(this).find('div.icon-dropdown > i').addClass('fa-caret-down');
        } else{
            $(this).find('div.icon-dropdown > i').addClass('fa-caret-up');
            $(this).find('div.icon-dropdown > i').removeClass('fa-caret-down');
        }
        
    });
    
    $('body').on('click','#logout',function(){
        if (confirm('Are You Sure You Want to Logout ?')){
            window.location.href = "{% url 'main_app:logout' %}"
        }
    });
});