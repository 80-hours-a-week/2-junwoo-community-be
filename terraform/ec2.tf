resource "aws_instance" "frontend" {
  ami           = "ami-0130d8d35bcd2d433" # Amazon Linux 2023 AMI
  instance_type = "t3.micro"
  key_name      = "Linuxkey"
  subnet_id     = data.aws_subnet.ap_northeast_2c.id

  vpc_security_group_ids = [aws_security_group.frontend_sg.id]

  tags = {
    Name = "FE"
  }
}

resource "aws_instance" "backend" {
  ami           = "ami-0130d8d35bcd2d433" # Amazon Linux 2023 AMI
  instance_type = "t3.micro"
  key_name      = "Linuxkey"
  subnet_id     = data.aws_subnet.ap_northeast_2c.id

  vpc_security_group_ids = [aws_security_group.backend_sg.id]

  tags = {
    Name = "BE"
  }
}
