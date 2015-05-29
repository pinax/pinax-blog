
$(document).ready(function  () {
	$("#id_teaser").on("propertychange change keyup paste input", function(){
		$("#id_description").val($("#id_teaser").val());
	});
});