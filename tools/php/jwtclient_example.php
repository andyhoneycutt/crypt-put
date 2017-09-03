<?php
require_once("class.jwtapibase.php");

$url = 'http://api.somewhere.in.the.universe.com/';
$username = 'myUsername';
$password = 'myPassword';

$client = new JWTApiBase($url, $username, $password);


// Perhaps we want to update the email address of user at 1234
$data = json_encode(array(
  'id' => '1234',
  'email_address' => 'me@andyhoneycutt.com'
));

// append the endpoint "user/" to our client base url, send our data to it
$response = $client->apiRequest($data, $client->getUrl('user/'));

// print out the repsonse
print_r($response);
print_r(json_decode($response));
