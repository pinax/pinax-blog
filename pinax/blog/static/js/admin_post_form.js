
var djJq = django.jQuery;

djJq(document).ready(function  () {
	djJq("#id_teaser").on("propertychange change keyup paste input", function(){
		djJq("#id_description").val(djJq("#id_teaser").val());
	});
})