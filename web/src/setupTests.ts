import fetchMock from 'fetch-mock';
import 'isomorphic-fetch';

// https://www.wheresrhys.co.uk/fetch-mock/
// If your Request object is not an instance of the Request constructor
// used by fetch-mock you need to set a reference to the request class.
fetchMock.config.Request = Request;
