TestCase('hello world',{
   "test 'hello world'==='hello world'":function(){
      assertEquals('Hello World','Hello World');
   }
   ,"test 'expected'==='actual'":function(){
      assertEquals('expected result','Actual result');
   }
   ,"test 'result'==='result'":function(){
      assertEquals('result','result');
   }
});