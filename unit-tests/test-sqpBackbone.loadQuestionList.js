
TestCase('test_sqpBackbone.loadQuestionList()',{
	
	// Test weather the sqpBackbone.responceHandler() return the payload from a standard responce.
	
	setUp:function() {
    	
	this.test_sqpBackbone = sqpBackbone;
	
	this.mock = sinon.mock(sqpBackbone);
		
	},

	tearDown:function() {
		
		delete this.test_sqpBackbone;
		delete this.mock;
	
	},
	
	"test sqpBackbone.loadQuestionList()'":function(){
		
		 
			
		 this.mock.expects("questionList").once();
		 
		 this.test_sqpBackbone.loadQuestionList();
		
		 this.mock.verify();
		
	}
   
});