#Required for each account
variable "external_id" {
}

#Create the role and setup the trust policy
resource "aws_iam_role" "dome9" {
  name               = "Dome9-Connect"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::634729597623:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "${var.external_id}"
        }
      }
    }
  ]
}
EOF

}

#Create the readonly policy
resource "aws_iam_policy" "readonly-policy" {
  name        = "Dome9-readonly-policy"
  description = ""
  policy      = file("readonly-policy.json")
}

#Create the write policy
resource "aws_iam_policy" "write-policy" {
  name        = "Dome9-write-policy"
  description = ""
  policy      = file("write-policy.json")
}

#Attach 4 policies to the cross-account role
resource "aws_iam_policy_attachment" "attach-d9-read-policy" {
  name       = "Attach-readonly"
  roles      = [aws_iam_role.dome9.name]
  policy_arn = aws_iam_policy.readonly-policy.arn
}

resource "aws_iam_policy_attachment" "attach-d9-write-policy" {
  name       = "Attach-write"
  roles      = [aws_iam_role.dome9.name]
  policy_arn = aws_iam_policy.write-policy.arn
}

resource "aws_iam_role_policy_attachment" "attach-security-audit" {
  role       = aws_iam_role.dome9.name
  policy_arn = "arn:aws:iam::aws:policy/SecurityAudit"
}

resource "aws_iam_role_policy_attachment" "attach-inspector-readonly" {
  role       = aws_iam_role.dome9.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonInspectorReadOnlyAccess"
}

#Output the role ARN
output "Role_ARN" {
  value = aws_iam_role.dome9.arn
}

