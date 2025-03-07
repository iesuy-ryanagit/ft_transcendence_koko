all:
	docker-compose build --no-cache
	docker-compose up

down:
	docker-compose down

clean:
	docker-compose down
	docker-compose rm -f

fclean: clean
	docker system prune -af

re: fclean all
