
sqpBackbone.collections.questionList = Backbone.Collection.extend({		
	page : 1,
	//completeness 0 = All Questions
    //completeness 1 = Complete Questions
    //completeness 2 = Todo Questions
	completeness: 0,
	MTMM: 0,
	study : '',
	language : '',
	country : '',
	model: sqpBackbone.models.questionItem,
	question: 0,
	url: '/sqp/api/questionList',
	meta: null,
	searchText : "",
	parse: function(response){
		if (response.success == "1"){
			this.meta = response.meta;
			return response.payload;
		} else {
			//Send the error off to the error handler
			sqpBackbone.helpers.handleServerError(response);
			
		}		
	},
	updateUrl : function updateUrl(silent) {
		var prevUrl = this.url;
		
		if(silent == undefined) {
			silent = false;
		}
		
		this.url = '/sqp/api/questionList?page=' + this.page;
		
		if(this.study != '') {
			this.url += '&studyId=' + this.study;
		}
		
		if(this.language != '') {
			this.url += '&languageIso=' + this.language;
		}
		
		if(this.country != '') {
			this.url += '&countryIso=' + this.country;
		}
		
		if(this.completeness != 0) {
			this.url += '&completeness=' + this.completeness;
		}
		
		if(this.MTMM != 0) {
			this.url += '&MTMM=' + this.MTMM;
		}
		
		if(this.searchText != "") {
			this.url += '&q=' + encodeURIComponent(this.searchText);
		}
		
		
		if (!silent && (prevUrl != this.url)) {
			this.trigger("loading", {});
			var collection=this;
			this.fetch({error: function () {
				
				//Send a notice that the load failed
				collection.trigger("failed", {});
			}});
		} 
	},
	setFromDict : function (queryDict, silent) {
		
		if(queryDict['page']) {
			this.page = 1 * queryDict['page']
		} else {
			this.page = 1;
		}
		
		if(queryDict['studyId']) {
			this.study = queryDict['studyId']
		} else {
			this.study = '';
		}
		
		if(queryDict['languageIso']) {
			this.language = queryDict['languageIso']
		} else {
			this.language = '';
		}
		
		if(queryDict['countryIso']) {
			this.country = queryDict['countryIso']
		} else {
			this.country = '';
		}
		
		if(queryDict['completeness']) {
			this.completeness = queryDict['completeness']
		} else {
			this.completeness = 0;
		}
		
		if(queryDict['MTMM']) {
			this.MTMM = queryDict['MTMM']
		} else {
			this.MTMM = 0;
		}
		
		if(queryDict['question']) {
			this.question = queryDict['question']
		} else {
			this.question = 0;
		}
		
		if(queryDict['q']) {
			this.searchText = decodeURIComponent(queryDict['q']);
		} else {
			this.searchText = "";
		}
		
		if (silent == undefined) {
			silent = false;
		}
		
		this.updateUrl(silent);
	},
	getURI : function getURI() {
		//Get a URI based on the search and page that we can use for the browser history object 
		//to go back and forward
		var uri = this.url.replace('/sqp/api/questionList?', '');
		uri = uri.replace(/&/g, '|');
		uri = uri.replace(/=/g, ':');
		uri = uri.replace('page:1|', '');
		uri = uri.replace(/page:1^/, '');
		
		if(this.question != 0) {
			if (uri != '') {
				uri += '|';
			}
			uri += 'question:' + this.question;
		}
		
		return uri;
	},
	setQuestion : function (questionId) {
		
		this.question = questionId;
	},
	nextPage : function nextPage (){
		if (this.page < this.meta.totalPages) {
			this.page += 1;
			this.updateUrl();
		}
	},
	prevPage : function prevPage (){
		if (this.page > 1) {
			this.page -= 1;
			this.updateUrl();
		}
	}, 
	setStudy: function setStudy(study) {
		if (this.study != study) {
			this.page = 1;
			this.study = study;
			this.updateUrl();
		}
	},
	setLanguage: function setLanguage(language) {
		if (this.language != language) {
			this.page = 1;
			this.language = language;
			this.updateUrl();
		}
	},
	setCountry: function setCountry(country) {
		if (this.country != country) {
			this.page = 1;
			this.country = country;
			this.updateUrl();
		}
	},
	setCompleteness : function setCompleteness(completeness) {
		if (this.completeness != completeness) {
			this.page = 1;
			this.completeness = completeness;
			this.updateUrl();
		}
	},
	setMTMM : function setMTMM(MTMM) {
		if (this.MTMM != MTMM) {
			this.page = 1;
			this.MTMM = MTMM;
			this.updateUrl();
		}
	}, 
	setSearchText : function setSearchText(text) {
		text = $.trim(text);
		
		if(this.searchText != text) {
			this.page = 1;
			this.searchText = text;
			this.updateUrl();
		}
		
	}
});




















