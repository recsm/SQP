
TestCase('test_sqpBackbone.responceHandler()',{
	
	// Test weather the sqpBackbone.responceHandler() return the payload from a standard responce.
	
	setUp:function() {
    	
		this.testdataSuccess = {
				"meta": {}, 
				"payload": {"testpayloadcontent": "testPhrase"}, 
				"success": 1
		};
		
		this.testResponce = sqpBackbone.responceHandler(this.testdataSuccess);
		
	},

	tearDown:function() {
		
	    delete this.testdata ;
	    delete this.testResponce;
	
	},
	
	"test sqpBackbone.responceHandler()'":function(){
	
		
		assertEquals(this.testResponce.testpayloadcontent ,"testPhrase");
		
	}
   
});