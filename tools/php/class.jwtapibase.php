<?php
define("URL_SUFFIX_AUTH", 'api-auth/');
define("PARAM_USERNAME", 'username');
define("PARAM_PASSWORD", 'password');

class JWTApiBase {
  private $_url;
  private $_token;

  public function __construct($url, $username, $password) {
    $this->_url = $url;
    $this->_token = $this->pullToken($username, $password);
  }

  public function getUrl($add = '') {
    return $this->_url . "$add";
  }

  private function getToken() {
    return $this->_token;
  }

  private function pullToken($username, $password) {
    $url = $this->getUrl(URL_SUFFIX_AUTH);

    $data = json_encode(array(
      PARAM_USERNAME => $username,
      PARAM_PASSWORD => $password
    ));

    $headers = array(
      "Content-type: application/json\r\n"
    );

    $response = json_decode($this->rawRequest($data, $headers, $url));
    try {
      $ret = $response->token;
    }
    catch(Exception $e) {
      $ret = null;
      error_log("Could not assign token from $url");
    }
    return $ret;
  }

  private function rawRequest($data, $headers, $url, $method='POST') {
    $options = array(
        'http' => array(
            'header' => $headers,
            'method' => $method,
            'content' => $data,
        ),
    );
    $context = stream_context_create($options);
    $result = file_get_contents($url, false, $context);
    return $result;
  }

  public function apiRequest($data, $url, $method='POST') {
    if( null === $this->getToken() ) {
      return null;
    }

    $headers = array(
      "Content-type: application/json",
      "Authorization: JWT {$this->getToken()}"
    );
    return $this->rawRequest($data, $headers, $url, $method);
  }
}
