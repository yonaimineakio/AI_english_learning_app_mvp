class ErrorResponseModel {
  const ErrorResponseModel({
    required this.detail,
    this.errorCode,
  });

  final String detail;
  final String? errorCode;

  factory ErrorResponseModel.fromJson(Map<String, dynamic> json) {
    return ErrorResponseModel(
      detail: json['detail'] as String? ?? 'Unknown error',
      errorCode: json['error_code'] as String?,
    );
  }
}


